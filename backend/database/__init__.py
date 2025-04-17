import sqlite3
from pathlib import Path
import os
from typing import Union
from .schema import criar_banco
from .seeds import popular_banco
from .queries import get_random_word, get_palavras_e_definicoes


# Caminho para o banco de dados (relativo ao arquivo atual)
DB_PATH = Path(__file__).parent / "banco_palavras.db"

def inicializar_banco(db_path: Union[str, Path]) -> bool:
    """
    Inicializa o banco de dados, criando se não existir e populando com dados iniciais
    
    Args:
        db_path: Caminho para o arquivo do banco de dados (str ou Path)
    
    Returns:
        bool: True se o banco foi inicializado com sucesso, False caso contrário
    """
    # Converte para string se for Path
    db_path_str = str(db_path) if isinstance(db_path, Path) else db_path
    
    try:
        if not os.path.exists(db_path_str):
            print(f"🔧 Criando novo banco em {db_path_str}...")
            
            # Cria as tabelas do banco
            if not criar_banco(db_path_str):
                print("❌ Falha ao criar as tabelas do banco")
                return False
            
            # Cria uma conexão para popular os dados
            conn = sqlite3.connect(db_path_str)
            
            # Popula com dados iniciais
            if not popular_banco(conn):
                print("❌ Falha ao popular o banco com dados iniciais")
                conn.close()
                return False
            
            conn.close()
            print("✅ Banco criado e populado com sucesso!")
            return True
        
        print(f"ℹ Banco já existe em {db_path_str}")
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico ao inicializar banco: {e}")
        return False

def get_db_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco configurada"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Para acesso por nome de coluna
    return conn

__all__ = [
    'get_random_word',
    'get_palavras_e_definicoes',
    'DB_PATH',
    'inicializar_banco',
    'get_db_connection'
]