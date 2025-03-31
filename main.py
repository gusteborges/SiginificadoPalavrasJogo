from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from backend.game.processamento import AvaliadorRespostas
from backend.database.schema import criar_banco

# Constantes
DB_PATH = "backend/database/banco_palavras.db"

# Modelos Pydantic
class PalavraResposta(BaseModel):
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

# Lifespan handler (substitui o on_event deprecated)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    try:
        # Cria ou verifica o banco
        if not criar_banco(DB_PATH):
            raise RuntimeError("Falha ao criar/verificar o banco de dados")
        
        # Treina o modelo com as definições
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT definicao FROM palavras")
        definicoes = [row["definicao"] for row in cursor.fetchall()]
        avaliador.treinar_modelo(definicoes)
        conn.close()
        
        print("✅ Sistema inicializado com sucesso")
        yield
    except Exception as e:
        raise RuntimeError(f"Falha na inicialização: {str(e)}")

# Cria a aplicação FastAPI com lifespan
app = FastAPI(lifespan=lifespan)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização do avaliador
avaliador = AvaliadorRespostas()

# Funções de banco de dados
def conectar_banco():
    """Cria conexão segura com o banco"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acesso por nome de coluna
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Erro ao conectar ao banco: {str(e)}")

def obter_frases(palavra_id: int):
    """Busca frases associadas a uma palavra"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT frase FROM frases WHERE palavra_id = ?", (palavra_id,))
        frases = [row["frase"] for row in cursor.fetchall()]
        conn.close()
        return frases
    except sqlite3.Error as e:
        print(f"⚠️ Erro ao buscar frases: {str(e)}")
        return []

def obter_palavra_aleatoria():
    """Busca uma palavra aleatória com todas as relações"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.palavra, p.definicao, p.dificuldade, c.nome as categoria
            FROM palavras p
            JOIN categorias c ON p.categoria_id = c.id
            ORDER BY RANDOM()
            LIMIT 1
        """)
        palavra = cursor.fetchone()
        
        if not palavra:
            conn.close()
            return None
        
        frases = obter_frases(palavra["id"])
        conn.close()
        
        return {
            "termo": palavra["palavra"],
            "categoria": palavra["categoria"],
            "definicao": palavra["definicao"],
            "dificuldade": palavra["dificuldade"],
            "frases": frases
        }
    except sqlite3.Error as e:
        raise RuntimeError(f"Erro ao buscar palavra: {str(e)}")

def buscar_palavra(termo: str):
    """Busca uma palavra específica com todas as relações"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.palavra, p.definicao, p.dificuldade, c.nome as categoria
            FROM palavras p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE LOWER(p.palavra) = LOWER(?)
        """, (termo.strip(),))
        
        palavra = cursor.fetchone()
        
        if not palavra:
            conn.close()
            return None
        
        frases = obter_frases(palavra["id"])
        conn.close()
        
        return {
            "termo": palavra["palavra"],
            "categoria": palavra["categoria"],
            "definicao": palavra["definicao"],
            "dificuldade": palavra["dificuldade"],
            "frases": frases
        }
    except sqlite3.Error as e:
        raise RuntimeError(f"Erro ao buscar palavra: {str(e)}")

# Endpoints
@app.get("/api/palavra-aleatoria", response_model=PalavraResposta)
async def palavra_aleatoria():
    palavra = obter_palavra_aleatoria()
    if not palavra:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma palavra encontrada no banco de dados"
        )
    return palavra

@app.post("/api/verificar", response_model=VerificacaoResposta)
async def verificar_resposta(request: VerificacaoRequest):
    try:
        palavra = buscar_palavra(request.palavra)
        if not palavra:
            raise HTTPException(
                status_code=404,
                detail=f"Palavra '{request.palavra}' não encontrada"
            )
        
        similaridade, acerto = avaliador.avaliar_resposta(
            request.resposta.lower().strip(),  # Normaliza a resposta
            palavra["definicao"].lower()      # Normaliza a definição
        )
        
        # Feedback mais detalhado
        if acerto:
            feedback = "✅ Resposta correta!"
        elif similaridade > 0.7:
            feedback = f"⚠️ Quase lá! ({similaridade:.0%} de similaridade)"
        elif similaridade > 0.4:
            feedback = f"❌ Incorreto, mas você está no caminho certo ({similaridade:.0%})"
        else:
            feedback = "❌ Resposta incorreta"
        
        return {
            "acerto": acerto,
            "similaridade": float(similaridade),
            "definicao_correta": None if acerto else palavra["definicao"],
            "feedback": feedback
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao verificar resposta: {str(e)}"
        )

def run_server():
    """Função para executar o servidor"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    run_server()