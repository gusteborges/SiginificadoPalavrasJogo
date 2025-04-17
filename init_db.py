from backend.database import inicializar_banco, DB_PATH
import os

def main():
    """Script para inicializar o banco de dados"""
    print("🔧 Iniciando criação do banco de dados...")
    
    # Remove o banco se existir
    if os.path.exists(DB_PATH):
        print("🗑 Removendo banco de dados existente...")
        os.remove(DB_PATH)
    
    # Inicializa o banco
    if inicializar_banco(DB_PATH):
        print("✅ Banco de dados criado e populado com sucesso!")
    else:
        print("❌ Erro ao criar banco de dados")

if __name__ == "__main__":
    main() 