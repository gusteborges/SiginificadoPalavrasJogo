from backend.database import inicializar_banco, DB_PATH, get_random_word
from backend.game.processamento import AvaliadorRespostas
from backend.database.queries import get_palavras_e_definicoes

def main():
    if not inicializar_banco(DB_PATH):
        print("❌ Falha ao inicializar o banco!")
        return

    avaliador = AvaliadorRespostas()
    definicoes = [item['definicao'] for item in get_palavras_e_definicoes(DB_PATH)]
    avaliador.treinar_modelo(definicoes)
    
    palavra = get_random_word(DB_PATH)
    if not palavra:
        print("❌ Não foi possível obter uma palavra do banco!")
        return
    
    print(f"\n=== Adivinhe o significado de: {palavra.palavra} ===")
    print(f"Dica: Pertence à categoria {palavra.categoria_nome}")
    
    if palavra.frases:
        print("\nContexto:")
        for i, frase in enumerate(palavra.frases[:2], 1):  # Mostra no máximo 2 frases
            print(f"{i}. {frase}")
    
    resposta = input("\nSua resposta: ").strip()
    
    similaridade, aceita = avaliador.avaliar_resposta(resposta, palavra.definicao)
    
    print(f"\nSimilaridade calculada: {similaridade:.0%}")
    if aceita:
        print("✅ Resposta aceita!")
    else:
        print("❌ Resposta parcialmente correta" if similaridade > 0.2 else "❌ Resposta incorreta")
    
    print(f"\nDefinição oficial: {palavra.definicao}")
    print(f"\nExplicação: Sua resposta contém {'alguns' if similaridade > 0.2 else 'poucos'} elementos corretos.")
    
    # Mostra palavras-chave encontradas
    palavras_relevantes = ["língua", "aumento", "anormal", "grande", "crescimento"]
    encontradas = [p for p in palavras_relevantes if p in resposta.lower()]
    if encontradas:
        print(f"Você usou termos relevantes: {', '.join(encontradas)}")

if __name__ == "__main__":
    main()