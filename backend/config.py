import os
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente
load_dotenv(find_dotenv())

# Constantes
DB_PATH = os.getenv('DB_PATH', "backend/database/banco_palavras.db") 