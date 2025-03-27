# Teste de funcionamento do sklearn (pode adicionar no main.py)
from backend.database import inicializar_banco, DB_PATH, get_random_word
from .backend.game.processamento import AvaliadorRespostas
from backend.database.queries import get_palavras_e_definicoes

def teste_sklearn():
    avaliador = AvaliadorRespostas()
    textos = [
        "aumento anormal da língua",
        "crescimento excessivo do órgão lingual",
        "doença que causa aumento da língua"
    ]
    avaliador.treinar_modelo(textos)
    
    # Teste com respostas conhecidas
    teste1 = avaliador.avaliar_resposta("língua grande", "aumento anormal da língua")
    teste2 = avaliador.avaliar_resposta("dor na garganta", "aumento anormal da língua")
    
    print("\n=== Teste do Sklearn ===")
    print(f"Resposta similar: {teste1} (esperado: alta similaridade)")
    print(f"Resposta diferente: {teste2} (esperado: baixa similaridade)")