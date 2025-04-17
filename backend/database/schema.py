import sqlite3
from pathlib import Path

def criar_banco(db_path: str) -> bool:
    """
    Cria o banco de dados com as tabelas necessárias se não existirem.
    Retorna True se sucesso, False se erro.
    """
    try:
        # Garante que o diretório existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria tabela de categorias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
        """)
        
        # Cria tabela de palavras
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palavra TEXT NOT NULL UNIQUE,
            definicao TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            dificuldade INTEGER DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """)
        
        # Cria tabela de frases
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS frases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palavra_id INTEGER NOT NULL,
            frase TEXT NOT NULL,
            gerada_automaticamente BOOLEAN DEFAULT TRUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (palavra_id) REFERENCES palavras (id)
        )
        """)

        # Cria tabela de variações aceitas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS variacoes_aceitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palavra_id INTEGER NOT NULL,
            variacao TEXT NOT NULL,
            FOREIGN KEY (palavra_id) REFERENCES palavras (id)
        )
        """)
        
        # Cria índices para melhor performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_palavras_categoria ON palavras (categoria_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_frases_palavra ON frases (palavra_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_variacoes_palavra ON variacoes_aceitas (palavra_id)")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco: {str(e)}")
        return False