import sqlite3
from pathlib import Path
from .schema import criar_banco
from .seeds import popular_banco
from .queries import get_random_word 

DB_PATH = Path(__file__).parent.parent / "banco_palavras.db"

def inicializar_banco():
    """Verifica e cria o banco se necessário"""
    if not DB_PATH.exists():
        print("🛠️ Banco não encontrado. Criando novo banco...")
        conn = criar_banco(DB_PATH)
        if conn:
            popular_banco(conn)
            conn.close()
    else:
        print("✅ Banco já existe. Prosseguindo...")

inicializar_banco()


__all__ = ['get_random_word', 'DB_PATH'] 