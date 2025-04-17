from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from backend.game.processamento import AvaliadorRespostas
from backend.game.gerador_frases import GeradorFrases as FraseGenerator
from backend.database.schema import criar_banco
from backend.config import DB_PATH
from dotenv import load_dotenv, find_dotenv
import os

# Carrega variáveis de ambiente
print("Carregando variáveis de ambiente...")
load_dotenv(find_dotenv())

# Modelos Pydantic
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

# Lifespan para limpar frases em dev
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Cria banco se necessário
    if not criar_banco(DB_PATH):
        raise RuntimeError("Falha ao criar banco")
    # Limpa frases existentes
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM frases;")
    conn.commit()
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia serviços
avaliador = AvaliadorRespostas()
gerador = FraseGenerator()

# Função de conexão
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/palavra-aleatoria", response_model=PalavraResposta)
def palavra_aleatoria():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT p.id, p.palavra, p.definicao, p.dificuldade, c.nome as categoria FROM palavras p JOIN categorias c ON p.categoria_id=c.id ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Nenhuma palavra encontrada")
    
    # busca frase inicial
    cur.execute("SELECT frase FROM frases WHERE palavra_id=? ORDER BY rowid LIMIT 1", (row['id'],))
    initial = [r['frase'] for r in cur.fetchall()]
    if not initial:
        # gera e salva frase inicial
        frase0 = gerador.gerar_frase_unica(row['palavra'], row['definicao'], row['categoria'])
        cur.execute("INSERT INTO frases(palavra_id, frase) VALUES(?,?)", (row['id'], frase0))
        conn.commit()
        frases = [frase0]
    else:
        frases = initial
    conn.close()
    return {
        "id": row['id'],
        "termo": row['palavra'],
        "categoria": row['categoria'],
        "definicao": row['definicao'],
        "dificuldade": row['dificuldade'],
        "frases": frases,
    }

@app.post("/api/verificar", response_model=VerificacaoResposta)
def verificar(request: VerificacaoRequest):
    palavra = request.palavra.strip()
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT definicao FROM palavras WHERE LOWER(palavra)=LOWER(?)", (palavra,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, f"Palavra '{palavra}' não encontrada")
    sim, ok = avaliador.avaliar_resposta(request.resposta.lower().strip(), row['definicao'].lower())
    feedback = (
        "✅ Correto!" if ok else
        f"⚠️ Quase! ({sim:.0%})" if sim>0.7 else
        "❌ Incorreto"
    )
    return {"acerto": ok, "similaridade": sim, "definicao_correta": None if ok else row['definicao'], "feedback": feedback}

@app.post("/api/gerar-frase", response_model=GerarFraseResponse)
def gerar_frase(request: GerarFraseRequest):
    conn = conectar()
    cur = conn.cursor()
    
    # busca frases existentes
    cur.execute("SELECT frase FROM frases WHERE palavra_id=? ORDER BY rowid", (request.palavra_id,))
    todas = [r['frase'] for r in cur.fetchall()]
    total = len(todas)
    
    # Se já tem 4 frases (1 inicial + 3 extras), retorna a última
    if total >= 4:
        conn.close()
        return {"frase": todas[-1], "frases_restantes": 0}
    
    # Tenta gerar nova frase via IA
    for _ in range(3):  # tenta até 3 vezes
        try:
            nova = gerador.gerar_frase_unica(request.palavra, request.definicao, request.categoria)
            if nova and not nova in todas:  # verifica se é válida e não duplicada
                cur.execute("INSERT INTO frases(palavra_id, frase) VALUES(?,?)", (request.palavra_id, nova))
                conn.commit()
                restantes = max(0, 3 - (total))  # calcula frases restantes (excluindo a primeira)
                conn.close()
                return {"frase": nova, "frases_restantes": restantes}
        except Exception as e:
            print(f"Erro ao gerar frase: {e}")
            continue
    
    # Se não conseguiu gerar nova frase, retorna a última existente
    if todas:
        return {"frase": todas[-1], "frases_restantes": max(0, 3 - (total-1))}
    
    raise HTTPException(500, "Não foi possível gerar uma nova frase")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
