from fastapi import APIRouter, HTTPException
from backend.database import get_palavra_por_termo
from backend.game.processamento import AvaliadorRespostas
from .models import VerificacaoRequest, VerificacaoResposta


router = APIRouter(prefix="/api")

@router.post("/verificar", response_model=VerificacaoResposta)
async def verificar_resposta(request: VerificacaoRequest):
    try:
        palavra = get_palavra_por_termo(DB_PATH, request.palavra)
        if not palavra:
            raise HTTPException(status_code=404, detail="Palavra não encontrada")
        
        similaridade, aceita = avaliador.avaliar_resposta(request.resposta, palavra.definicao)
        
        return {
            "acerto": aceita,
            "similaridade": float(similaridade),
            "definicao_correta": palavra.definicao if not aceita else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    