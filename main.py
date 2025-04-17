from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from backend.game.processamento import AvaliadorRespostas
from backend.game.gerador_frases import GeradorFrases
from backend.database.schema import criar_banco
from dotenv import load_dotenv, find_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
print("Carregando variáveis de ambiente...")
load_dotenv(find_dotenv())

# Constantes
DB_PATH = os.getenv('DB_PATH', "backend/database/banco_palavras.db")

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

# Lifespan handler (substitui o on_event deprecated)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    try:
        print("Iniciando aplicação...")
        # Limpa a tabela de frases ao iniciar
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM frases;")
        conn.commit()
        conn.close()
        
        yield  # Este yield é obrigatório
        
        print("Encerrando aplicação...")
    except Exception as e:
        print(f"Erro na inicialização: {str(e)}")
        raise

# Cria a aplicação FastAPI com lifespan
app = FastAPI(lifespan=lifespan)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização dos serviços
avaliador = AvaliadorRespostas()
gerador_frases = GeradorFrases()

# Funções de banco de dados
def conectar_banco():
    """Cria conexão segura com o banco"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acesso por nome de coluna
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Erro ao conectar ao banco: {str(e)}")

def obter_frases(palavra_id: int, palavra: str, definicao: str, categoria: str) -> List[str]:
    """Busca frases associadas a uma palavra ou gera novas se necessário"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Busca todas as frases que NÃO são a frase padrão
        cursor.execute("""
            SELECT frase FROM frases 
            WHERE palavra_id = ? 
            AND frase NOT LIKE 'Esta é uma frase de exemplo%'
            AND frase NOT LIKE 'Aqui está outro exemplo%'
            ORDER BY rowid
        """, (palavra_id,))
        frases_reais = [row["frase"] for row in cursor.fetchall()]
        
        # Se não houver frases reais, gera novas usando o gerador
        if not frases_reais:
            try:
                frases_reais = gerador_frases.gerar_frases(palavra, definicao, categoria, palavra_id)
            except Exception as e:
                print(f"⚠️ Erro ao gerar frases iniciais: {str(e)}")
                # Em caso de erro, usa frases padrão
                frases_reais = [
                    f"Esta é uma frase de exemplo usando a palavra '{palavra}'.",
                    f"Aqui está outro exemplo com '{palavra}'.",
                    f"E esta é a terceira frase com '{palavra}'."
                ]
        
        conn.close()
        return frases_reais
        
    except sqlite3.Error as e:
        print(f"⚠️ Erro ao buscar/salvar frases: {str(e)}")
        return [f"Esta é uma frase de exemplo usando a palavra '{palavra}'."]

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
        
        frases = obter_frases(palavra["id"], palavra["palavra"], palavra["definicao"], palavra["categoria"])
        conn.close()
        
        return {
            "id": palavra["id"],
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
        
        frases = obter_frases(palavra["id"], palavra["palavra"], palavra["definicao"], palavra["categoria"])
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

@app.post("/api/gerar-frase", response_model=GerarFraseResponse)
async def gerar_frase(request: GerarFraseRequest):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Verifica quantas frases reais já existem para esta palavra
        cursor.execute("""
            SELECT frase FROM frases 
            WHERE palavra_id = ? 
            AND frase NOT LIKE 'Esta é uma frase de exemplo%'
            AND frase NOT LIKE 'Aqui está outro exemplo%'
            ORDER BY rowid
        """, (request.palavra_id,))
        frases_existentes = [row["frase"] for row in cursor.fetchall()]
        total_frases_geradas = len(frases_existentes)

        # Se já temos 3 ou mais frases, retorna a última
        if total_frases_geradas >= 3:
            conn.close()
            return {
                "frase": frases_existentes[-1],
                "frases_restantes": 0
            }

        # Se precisamos de mais frases, geramos todas de uma vez
        try:
            novas_frases = gerador_frases.gerar_frases(
                request.palavra,
                request.definicao,
                request.categoria,
                request.palavra_id
            )
            
            # Retorna a primeira frase nova que não existe ainda
            for frase in novas_frases:
                if frase not in frases_existentes:
                    frases_restantes = max(0, 2 - total_frases_geradas)
                    conn.close()
                    return {
                        "frase": frase,
                        "frases_restantes": frases_restantes
                    }
            
            # Se não encontrou frase nova, usa uma genérica
            frase = f"Aqui está outro exemplo usando '{request.palavra}'."
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar frase: {str(e)}")
            frase = f"Aqui está outro exemplo usando '{request.palavra}'."
            
            # Salva a frase genérica no banco
            cursor.execute(
                "INSERT INTO frases (palavra_id, frase) VALUES (?, ?)",
                (request.palavra_id, frase)
            )
            conn.commit()
        
        # Retorna a frase e quantas ainda podem ser geradas
        frases_restantes = max(0, 2 - total_frases_geradas)
        conn.close()
        
        return {
            "frase": frase,
            "frases_restantes": frases_restantes
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"⚠️ Erro no endpoint gerar-frase: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar frase: {str(e)}"
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