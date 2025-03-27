import sqlite3
from typing import Optional
from .models import Palavra, Categoria

def get_random_word(conn, categoria: Optional[str] = None) -> Optional[Palavra]:
    """Busca uma palavra aleatória com frases relacionadas"""
    query = """
        SELECT p.*, GROUP_CONCAT(f.frase, '|||') as frases
        FROM palavras p
        LEFT JOIN frases f ON p.id = f.palavra_id
    """
    
    params = []
    if categoria:
        query += " WHERE p.categoria_id = (SELECT id FROM categorias WHERE nome = ?)"
        params.append(categoria)
    
    query += " GROUP BY p.id ORDER BY RANDOM() LIMIT 1"
    
    try:
        conn.row_factory = sqlite3.Row
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
            frases=result['frases'].split('|||') if result['frases'] else []
        )
        
    except Exception as e:
        print(f"Erro na consulta: {e}")
        return None