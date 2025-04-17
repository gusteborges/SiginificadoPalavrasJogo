import sqlite3
from sqlite3 import Error

def popular_banco(db_path):
    """Popula o banco com dados iniciais"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Inserir categorias
        categorias = [
            (1, "Substantivos", "Palavras que nomeiam seres, objetos, lugares, etc."),
            (2, "Verbos", "Palavras que indicam ações"),
            (3, "Adjetivos", "Palavras que qualificam substantivos"),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO categorias (id, nome, descricao) VALUES (?, ?, ?)",
            categorias
        )

        # Inserir palavras
        palavras = [
            (1, "Resiliente", "Capaz de se recuperar facilmente de situações difíceis", 3, 3),
            (2, "Efêmero", "Que dura pouco tempo; passageiro, temporário", 3, 4),
            (3, "Pragmático", "Que se preocupa com aspectos práticos e resultados", 3, 3),
            (4, "Altruísta", "Que se dedica ao bem-estar dos outros", 3, 3),
            (5, "Perspicaz", "Que percebe as coisas com rapidez e clareza", 3, 4)
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO palavras (id, palavra, definicao, categoria_id, dificuldade) VALUES (?, ?, ?, ?, ?)",
            palavras
        )

        # Inserir frases de exemplo
        frases = [
            (1, "Ela é uma pessoa resiliente que superou muitas dificuldades.", 1),
            (2, "A beleza das flores é efêmera, dura apenas alguns dias.", 2),
            (3, "Ele tem uma visão pragmática dos negócios.", 3),
            (4, "O trabalho voluntário revela seu espírito altruísta.", 4),
            (5, "Sua análise perspicaz da situação impressionou a todos.", 5)
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO frases (id, frase, palavra_id) VALUES (?, ?, ?)",
            frases
        )

        conn.commit()
        print("✅ Dados inseridos com sucesso!")
        return True

    except Error as e:
        print(f"❌ Erro ao popular banco: {e}")
        return False

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    DB_PATH = "backend/database/banco_palavras.db"
    popular_banco(DB_PATH) 