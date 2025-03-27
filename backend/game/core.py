# backend/game/core.py
from backend.database.queries import get_palavras_e_definicoes
from backend.game.processamento import ProcessadorTexto

class Jogo:
    def __init__(self, db_path: str):
        self.dados = get_palavras_e_definicoes(db_path)
        self.processador = ProcessadorTexto()
        self._treinar_processador()
    
    def _treinar_processador(self):
        """Treina o modelo com todas as definições do banco"""
        definicoes = [item["definicao"] for item in self.dados]
        self.processador.treinar_modelo(definicoes)
    
    def avaliar_resposta(self, palavra_alvo: str, resposta_jogador: str) -> float:
        """Compara a resposta com a definição correta"""
        definicao_correta = next(
            item["definicao"] for item in self.dados 
            if item["palavra"] == palavra_alvo
        )
        return self.processador.comparar_textos(resposta_jogador, definicao_correta)