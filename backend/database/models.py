from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Categoria:
    id: int
    nome: str
    descricao: Optional[str] = None

@dataclass
class Palavra:
    id: int
    palavra: str
    definicao: str
    categoria_id: int
    dificuldade: int
    frases: List[str] = None
    variacoes: List[str] = None
    categoria_nome: Optional[str] = None  

@dataclass
class Frase:
    id: int
    conteudo: str
    palavra_id: int

@dataclass
class VariacaoAceita:
    id: int
    variacao: str
    palavra_id: int