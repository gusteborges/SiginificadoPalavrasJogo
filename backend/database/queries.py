import sqlite3
from pathlib import Path
from typing import Optional, List, Dict
from .models import Palavra, Categoria

def get_db_connection(db_path: str | Path):
    """Cria e retorna uma conexão com o banco configurada"""
    conn = sqlite3.connect(str(db_path) if isinstance(db_path, Path) else db_path)
    conn.row_factory = sqlite3.Row  # Para acesso por nome de coluna
    return conn

def get_random_word(db_path: str | Path, categoria: Optional[str] = None) -> Optional[Palavra]:
    """
    Busca uma palavra aleatória com frases relacionadas
    Args:
        db_path: Caminho para o banco de dados (str ou Path)
        categoria: Nome da categoria para filtrar (opcional)
    Returns:
        Objeto Palavra com frases ou None se erro
    """
    query = """
        SELECT 
            p.id,
            p.palavra,
            p.definicao,
            p.categoria_id,
            p.dificuldade,
            c.nome as categoria_nome,
            GROUP_CONCAT(f.frase, '|||') as frases
        FROM palavras p
        JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN frases f ON p.id = f.palavra_id
    """
    
    params = []
    if categoria:
        query += " WHERE c.nome = ?"
        params.append(categoria)
    
    query += " GROUP BY p.id ORDER BY RANDOM() LIMIT 1"
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return Palavra(
                id=result['id'],
                palavra=result['palavra'],
                definicao=result['definicao'],
                categoria_id=result['categoria_id'],
                dificuldade=result['dificuldade'],
                categoria_nome=result['categoria_nome'],
                frases=result['frases'].split('|||') if result['frases'] else []
            )
            
    except sqlite3.Error as e:
        print(f"Erro SQL ao buscar palavra: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

def get_palavras_e_definicoes(db_path: str | Path) -> List[Dict[str, str]]:
    """Retorna todas as palavras e definições do banco"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.palavra, p.definicao, c.nome as categoria 
                FROM palavras p
                JOIN categorias c ON p.categoria_id = c.id
            """)
            return [
                {
                    "palavra": row['palavra'],
                    "definicao": row['definicao'],
                    "categoria": row['categoria']
                }
                for row in cursor.fetchall()
            ]
    except sqlite3.Error as e:
        print(f"Erro SQL ao listar palavras: {e}")
        return []
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return []
    
# backend/database/queries.py
def get_categorias(db_path: str | Path) -> List[Dict[str, any]]:
    """Retorna todas as categorias cadastradas"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, descricao FROM categorias")
            return [
                {
                    "id": row['id'],
                    "nome": row['nome'],
                    "descricao": row['descricao']
                }
                for row in cursor.fetchall()
            ]
    except sqlite3.Error as e:
        print(f"Erro ao buscar categorias: {e}")
        return []