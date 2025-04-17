from backend.database import DB_PATH
import sqlite3
from typing import Dict, List
import os
from dotenv import load_dotenv, find_dotenv

# Carrega variáveis de ambiente
load_dotenv(find_dotenv())
DB_PATH = os.getenv('DB_PATH', "backend/database/banco_palavras.db")

def mostrar_palavras_com_variações():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
            cursor = conn.cursor()
            
            # Debug: Verificar tabelas existentes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            print("=== Tabelas existentes ===")
            for table in cursor.fetchall():
                print(table['name'])
            
            # Consulta principal com LEFT JOIN para incluir palavras sem variações
            cursor.execute("""
                SELECT 
                    p.id,
                    p.palavra,
                    p.definicao,
                    c.nome as categoria,
                    GROUP_CONCAT(v.variacao, '||') as variacoes,
                    f.frase as frase
                FROM palavras p
                JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN variacoes_aceitas v ON p.id = v.palavra_id
                JOIN frases f ON p.id = f.palavra_id
                GROUP BY p.id
            """)
            
            
            print("\n=== Palavras e variações ===")
            for row in cursor.fetchall():
                print(f"\nID: {row['id']}")
                print(f"Palavra: {row['palavra']}")
                print(f"Definição: {row['definicao']}")
                print(f"Categoria: {row['categoria']}")
                
                # Tratar caso onde não há variações
                variacoes = row['variacoes'].split('||') if row['variacoes'] else []
                print("Variações aceitas:")
                for i, variacao in enumerate(variacoes, 1):
                    print(f"  {i}. {variacao}")
                    
    except sqlite3.Error as e:
        print(f"Erro de banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def buscar_todas_frases() -> Dict[str, List[str]]:
    """
    Busca todas as frases de todas as palavras no banco.
    
    Returns:
        Dicionário onde a chave é a palavra e o valor é uma lista de frases
    """
    try:
        # Conecta ao banco
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Busca palavras e suas frases
        cursor.execute("""
            SELECT 
                p.palavra,
                p.definicao,
                c.nome as categoria,
                GROUP_CONCAT(f.frase, ' ||| ') as frases
            FROM palavras p
            JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN frases f ON p.id = f.palavra_id
            GROUP BY p.id
            ORDER BY p.palavra
        """)
        
        resultados = {}
        
        for row in cursor.fetchall():
            palavra = row['palavra']
            definicao = row['definicao']
            categoria = row['categoria']
            frases = row['frases'].split(' ||| ') if row['frases'] else []
            
            resultados[palavra] = {
                'definicao': definicao,
                'categoria': categoria,
                'frases': frases
            }
        
        conn.close()
        return resultados
        
    except sqlite3.Error as e:
        print(f"Erro ao buscar frases: {str(e)}")
        return {}

if __name__ == "__main__":
    mostrar_palavras_com_variações()
    print("Buscando todas as frases do banco...")
    resultados = buscar_todas_frases()
    
    # Imprime os resultados de forma organizada
    for palavra, info in resultados.items():
        print(f"\n{'='*50}")
        print(f"Palavra: {palavra}")
        print(f"Categoria: {info['categoria']}")
        print(f"Definição: {info['definicao']}")
        print("\nFrases:")
        for i, frase in enumerate(info['frases'], 1):
            print(f"{i}. {frase}")