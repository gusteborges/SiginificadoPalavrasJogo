from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Tuple, List

class AvaliadorRespostas:
    def __init__(self):
        # Configuração otimizada sem warnings
        self.vectorizer = TfidfVectorizer(
            preprocessor=self._preprocessar_texto,
            tokenizer=None,  # Usa o padrão agora
            token_pattern=r'(?u)\b\w\w+\b',  # Padrão para palavras com 2+ caracteres
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            stop_words=None
        )
        
    def _preprocessar_texto(self, texto: str) -> str:
        """Pré-processamento completo"""
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', '', texto)  # Remove pontuação
        texto = re.sub(r'\d+', '', texto)  # Remove números
        return texto
    
    def treinar_modelo(self, textos: List[str]):
        """Treina o modelo com tratamento de erros"""
        try:
            self.vectorizer.fit(textos)
        except ValueError as e:
            print(f"Aviso: {str(e)}")
            print("Usando fallback simplificado...")
            self._usar_fallback = True
    
    def avaliar_resposta(self, resposta: str, definicao_correta: str) -> Tuple[float, bool]:
        """Avaliação robusta com fallback"""
        # Pré-processamento
        resposta_pp = self._preprocessar_texto(resposta)
        definicao_pp = self._preprocessar_texto(definicao_correta)
        
        # Método 1: Similaridade de cosseno
        try:
            vetores = self.vectorizer.transform([resposta_pp, definicao_pp])
            similaridade = cosine_similarity(vetores[0], vetores[1])[0][0]
        except (ValueError, AttributeError):
            similaridade = 0.0
        
        # Método 2: Palavras-chave (fallback)
        palavras_chave = ["língua", "aumento", "anormal", "crescimento", "macroglossia"]
        acertos = sum(1 for p in palavras_chave if p in resposta_pp)
        similaridade_keywords = acertos / len(palavras_chave)
        
        # Combina os métodos
        similaridade_final = max(similaridade, similaridade_keywords)
        return similaridade_final, similaridade_final > 0.5