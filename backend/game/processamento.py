from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Tuple, List

class AvaliadorRespostas:
    def __init__(self):
        # Configuração do vetor TF-IDF
        self.vectorizer = TfidfVectorizer(
            preprocessor=self._preprocessar_texto,
            token_pattern=r'(?u)\b\w\w+\b',  # Detecta palavras com 2+ caracteres
            ngram_range=(1, 2),  # Considera unigramas e bigramas
            min_df=1,
            max_df=0.85,  # Evita termos muito frequentes que não ajudam na distinção
            stop_words="english"  # Remove palavras irrelevantes se em inglês
        )
        self.modelo_treinado = False  # Flag para indicar se o modelo foi treinado

    def _preprocessar_texto(self, texto: str) -> str:
        """Pré-processamento: minúsculas, remoção de pontuação e números"""
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', '', texto)  # Remove pontuação
        texto = re.sub(r'\d+', '', texto)  # Remove números
        return texto

    def treinar_modelo(self, textos: List[str]):
        """Treina o modelo e lida com falhas"""
        try:
            self.vectorizer.fit(textos)
            self.modelo_treinado = True
        except ValueError as e:
            print(f"Aviso: {str(e)} - Ajustando fallback para palavras-chave.")
            self.modelo_treinado = False

    def extrair_palavras_chave(self, texto: str, top_n=5) -> List[str]:
        """Gera palavras-chave dinamicamente a partir da definição correta"""
        palavras = texto.split()
        return list(set(palavras[:top_n]))  # Pega as primeiras N palavras únicas

    def avaliar_resposta(self, resposta: str, definicao_correta: str) -> Tuple[float, bool]:
        """Avalia a resposta com dois métodos: similaridade de cosseno e palavras-chave"""
        resposta_pp = self._preprocessar_texto(resposta)
        definicao_pp = self._preprocessar_texto(definicao_correta)

        # Método 1: Similaridade de cosseno
        similaridade = 0.0
        if self.modelo_treinado and hasattr(self.vectorizer, "vocabulary_"):
            try:
                vetores = self.vectorizer.transform([resposta_pp, definicao_pp])
                similaridade = cosine_similarity(vetores[0], vetores[1])[0][0]
            except ValueError:
                print("Erro ao calcular similaridade. Aplicando fallback.")

        # Método 2: Palavras-chave dinâmicas
        palavras_chave = self.extrair_palavras_chave(definicao_correta)
        acertos = sum(1 for p in palavras_chave if p in resposta_pp)
        similaridade_keywords = acertos / len(palavras_chave) if palavras_chave else 0.0

        # Combina os métodos
        similaridade_final = max(similaridade, similaridade_keywords)
        return similaridade_final, similaridade_final > 0.5
