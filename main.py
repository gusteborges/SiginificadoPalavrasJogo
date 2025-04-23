from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import time
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from backend.game.processamento import AvaliadorRespostas
from backend.game.gerador_frases import GeradorFrases  # Modelo remoto (Mistral/Gemini)
from backend.database.schema import criar_banco
from backend.config import DB_PATH
from dotenv import load_dotenv, find_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv(find_dotenv())

# FastAPI com lifespan para criar banco e limpar frases em dev
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not criar_banco(DB_PATH):
        raise RuntimeError("Falha ao criar banco")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM frases;")
    conn.commit()
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serviços
avaliador = AvaliadorRespostas()
gerador = GeradorFrases()

# Modelos Pydantic
default_response_frases = List[str]

class PalavraResposta(BaseModel):
    id: int
    termo: str
    categoria: str
    definicao: str
    frases: List[str] = []
    dificuldade: Optional[int] = None

class VerificacaoRequest(BaseModel):
    palavra: str
    resposta: str

class VerificacaoResposta(BaseModel):
    acerto: bool
    similaridade: float
    definicao_correta: Optional[str] = None
    feedback: str

class GerarFraseRequest(BaseModel):
    palavra_id: int
    palavra: str
    definicao: str
    categoria: str

class GerarFraseResponse(BaseModel):
    frase: str
    frases_restantes: int

# Conexão SQLite
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# GET /api/palavra-aleatoria
@app.get("/api/palavra-aleatoria", response_model=PalavraResposta)
def palavra_aleatoria():
    print("[DEBUG] Iniciando busca de palavra aleatória")
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT p.id, p.palavra, p.definicao, p.dificuldade, c.nome as categoria
            FROM palavras p
            JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN (
                SELECT palavra_id, COUNT(*) AS cnt FROM frases GROUP BY palavra_id
            ) f ON p.id = f.palavra_id
            WHERE IFNULL(f.cnt,0) < 4
            ORDER BY RANDOM() LIMIT 1
            """,
        )
        row = cur.fetchone()
        print("[DEBUG] Resultado da query:", dict(row) if row else None)
        
        if not row:
            print("[DEBUG] Nenhuma palavra encontrada")
            conn.close()
            raise HTTPException(status_code=404, detail="Todas as palavras completaram as frases")

        # Busca frases existentes
        cur.execute(
            "SELECT frase FROM frases WHERE palavra_id=? ORDER BY rowid ASC", (row['id'],)
        )
        frases = [r['frase'] for r in cur.fetchall()]
        print("[DEBUG] Frases encontradas:", frases)

        # Se não tem nenhuma frase, gera a frase inicial
        if not frases:
            print(f"[DEBUG] Gerando frase inicial para palavra ID={row['id']}")
            frase_inicial = gerar_com_retry(row['palavra'], row['definicao'], row['categoria'])
            cur.execute(
                "INSERT INTO frases(palavra_id, frase) VALUES(?,?)",
                (row['id'], frase_inicial)
            )
            conn.commit()
            frases = [frase_inicial]
            print(f"[DEBUG] Frase inicial gerada: {frase_inicial}")

        resposta = {
            "id": row['id'],
            "termo": row['palavra'],
            "categoria": row['categoria'],
            "definicao": row['definicao'],
            "dificuldade": row['dificuldade'],
            "frases": frases,
        }
        print("[DEBUG] Resposta final:", resposta)
        conn.close()
        return resposta
    except Exception as e:
        print(f"[ERROR] Erro ao buscar palavra aleatória: {str(e)}")
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# POST /api/verificar
@app.post("/api/verificar", response_model=VerificacaoResposta)
def verificar(request: VerificacaoRequest):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "SELECT definicao FROM palavras WHERE LOWER(palavra)=LOWER(?)", (request.palavra.strip(),)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Palavra '{request.palavra}' não encontrada")
    sim, ok = avaliador.avaliar_resposta(
        request.resposta.lower().strip(), row['definicao'].lower()
    )
    feedback = (
        "✅ Correto!" if ok else
        f"⚠️ Quase! ({sim:.0%})" if sim > 0.7 else
        "❌ Incorreto"
    )
    return {"acerto": ok, "similaridade": sim, "definicao_correta": None if ok else row['definicao'], "feedback": feedback}

# Helper: geração com retry e fallback simples
def gerar_com_retry(palavra: str, definicao: str, categoria: str, max_retries: int = 5):
    delay = 1
    for tentativa in range(1, max_retries + 1):
        try:
            return gerador.gerar_frase_unica(palavra, definicao, categoria)
        except Exception as e:
            print(f"[WARN] tentativa {tentativa} falhou: {e}")
            time.sleep(delay)
            delay *= 2
    # fallback: frase genérica
    print("[INFO] fallback genérico acionado")
    return f"Exemplo usando a palavra '{palavra}'."

# POST /api/gerar-frase
@app.post("/api/gerar-frase", response_model=GerarFraseResponse)
def gerar_frase(request: GerarFraseRequest):
    conn = conectar()
    try:
        conn.execute("BEGIN EXCLUSIVE")
        cur = conn.cursor()
        # conta frases existentes
        cur.execute("SELECT COUNT(*) as total FROM frases WHERE palavra_id=?", (request.palavra_id,))
        total = cur.fetchone()["total"]
        if total >= 4:
            cur.execute(
                "SELECT frase FROM frases WHERE palavra_id=? ORDER BY rowid DESC LIMIT 1", (request.palavra_id,)
            )
            ultima = cur.fetchone()["frase"]
            conn.commit()
            return {"frase": ultima, "frases_restantes": 0}
        # gerar
        nova = gerar_com_retry(request.palavra, request.definicao, request.categoria)
        cur.execute(
            "INSERT OR IGNORE INTO frases(palavra_id, frase) VALUES(?,?)", (request.palavra_id, nova)
        )
        conn.commit()
        cur.execute("SELECT COUNT(*) as total FROM frases WHERE palavra_id=?", (request.palavra_id,))
        novo_total = cur.fetchone()["total"]
        restantes = max(0, 4 - novo_total)
        return {"frase": nova, "frases_restantes": restantes}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] gerar-frase: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
