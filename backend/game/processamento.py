from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import unicodedata
from typing import Tuple, List
from nltk.stem import RSLPStemmer


class AvaliadorRespostas:
    def __init__(self):
        # Configuração otimizada para português
        self.vectorizer = TfidfVectorizer(
            preprocessor=self._preprocessar_texto,
            token_pattern=r'(?u)\b\w{3,}\b',  # Palavras com 3+ caracteres
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            stop_words=None  # Removido para português
        )
        self.stemmer = RSLPStemmer()
        self.modelo_treinado = False
        self.definicoes_vetorizadas = {}  # Cache de vetores das definições

    def _preprocessar_texto(self, texto: str) -> str:
        """Pré-processamento aprimorado para português"""
        if not isinstance(texto, str):
            return ""
        
        texto = texto.lower()
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')  # Remove acentos
        texto = re.sub(r'[\d]', '', texto)  # Remove números
        texto = re.sub(r'[\W]', ' ', texto)  # Remove caracteres especiais
        return texto.strip()

    def treinar_modelo(self, textos: List[str]):
        """Treina o modelo removendo duplicatas e entradas vazias"""
        if not textos:
            self.modelo_treinado = False
            return
        
        try:
            textos_validos = list(set(filter(lambda t: isinstance(t, str) and t.strip(), textos)))
            if textos_validos:
                self.vectorizer.fit(textos_validos)
                self.modelo_treinado = True
            else:
                self.modelo_treinado = False
        except Exception as e:
            print(f"Erro no treinamento: {str(e)}")
            self.modelo_treinado = False

    def _calcular_similaridade(self, resposta: str, definicao: str) -> float:
        """Calcula similaridade aproveitando vetores pré-gerados"""
        try:
            if not self.modelo_treinado:
                return self._similaridade_simples(resposta, definicao)

            if definicao not in self.definicoes_vetorizadas:
                self.definicoes_vetorizadas[definicao] = self.vectorizer.transform([definicao])

            vetor_resposta = self.vectorizer.transform([resposta])
            return cosine_similarity(vetor_resposta, self.definicoes_vetorizadas[definicao])[0][0]
        except Exception:
            return self._similaridade_simples(resposta, definicao)

    def _similaridade_simples(self, resposta: str, definicao: str) -> float:
        """Fallback melhorado com stemming"""
        resposta_palavras = {self.stemmer.stem(p) for p in self._preprocessar_texto(resposta).split()}
        definicao_palavras = {self.stemmer.stem(p) for p in self._preprocessar_texto(definicao).split()}
        
        if not definicao_palavras:
            return 0.0

        intersecao = resposta_palavras & definicao_palavras
        return len(intersecao) / len(definicao_palavras)

    def avaliar_resposta(self, resposta: str, definicao_correta: str) -> Tuple[float, bool]:
        """Avaliação robusta com múltiplas estratégias"""
        if not resposta or not definicao_correta:
            return 0.0, False
        
        resposta_pp = self._preprocessar_texto(resposta)
        definicao_pp = self._preprocessar_texto(definicao_correta)
        
        # Combina similaridade vetorial e simples
        similaridade_vetorial = self._calcular_similaridade(resposta_pp, definicao_pp)
        similaridade_simples = self._similaridade_simples(resposta_pp, definicao_pp)
        similaridade_final = max(similaridade_vetorial, similaridade_simples)
        
        # Limiares ajustados
        limite_acerto = 0.65  # Mais sensível que 0.5
        return similaridade_final, similaridade_final > limite_acerto
