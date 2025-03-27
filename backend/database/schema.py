import sqlite3
from sqlite3 import Error

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT
    )""",
    
    """CREATE TABLE IF NOT EXISTS palavras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        palavra TEXT NOT NULL UNIQUE,
        definicao TEXT NOT NULL,
        categoria_id INTEGER,
        dificuldade INTEGER CHECK(dificuldade BETWEEN 1 AND 5),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )""",
    
    """CREATE TABLE IF NOT EXISTS frases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frase TEXT NOT NULL,
        palavra_id INTEGER NOT NULL,
        FOREIGN KEY (palavra_id) REFERENCES palavras(id)
    )""",
    
    """CREATE TABLE IF NOT EXISTS variacoes_aceitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        palavra_id INTEGER NOT NULL,
        variacao TEXT NOT NULL,
        FOREIGN KEY (palavra_id) REFERENCES palavras(id)
    )"""
]

def criar_banco(db_path):
    """Cria todas as tabelas do banco"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for table_schema in SCHEMA:
            cursor.execute(table_schema)
        
        conn.commit()
        print("✅ Banco criado com sucesso!")
        return conn
        
    except Error as e:
        print(f"❌ Erro ao criar banco: {e}")
        if conn:
            conn.close()
        return None