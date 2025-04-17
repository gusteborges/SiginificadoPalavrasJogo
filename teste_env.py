from dotenv import load_dotenv, find_dotenv
import os

print("1. Procurando arquivo .env...")
env_path = find_dotenv()
print(f"Arquivo .env encontrado em: {env_path}")

print("\n2. Carregando variáveis de ambiente...")
load_dotenv(env_path)

print("\n3. Verificando variáveis carregadas:")
print(f"GOOGLE_API_KEY: {'Encontrada' if 'GOOGLE_API_KEY' in os.environ else 'Não encontrada'}")
print(f"DB_PATH: {'Encontrada' if 'DB_PATH' in os.environ else 'Não encontrada'}")

print("\n4. Conteúdo da GOOGLE_API_KEY:")
api_key = os.environ.get('GOOGLE_API_KEY', 'Não definida')
if api_key != 'Não definida':
    print(f"Primeiros 10 caracteres: {api_key[:10]}...")
else:
    print("Chave não encontrada") 