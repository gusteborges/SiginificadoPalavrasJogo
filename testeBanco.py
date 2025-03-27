from backend.database import DB_PATH
import sqlite3

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
                    GROUP_CONCAT(v.variacao, '||') as variacoes
                FROM palavras p
                JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN variacoes_aceitas v ON p.id = v.palavra_id
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

if __name__ == "__main__":
    mostrar_palavras_com_variações()