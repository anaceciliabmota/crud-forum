from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resposta, Topico, Usuario
from app.routers.respostas import _to_response as resposta_to_response
from app.routers.topicos import _to_response as topico_to_response
from app.schemas import PerfilResponse, UsuarioPublicResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/{usuario_id}/perfil", response_model=PerfilResponse)
def get_perfil(usuario_id: int, db: Annotated[Session, Depends(get_db)]):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.ativo.is_(True)).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    topicos = (
        db.query(Topico)
        .filter(Topico.autor_id == usuario_id)
        .order_by(Topico.created_at.desc())
        .limit(50)
        .all()
    )
    respostas = (
        db.query(Resposta)
        .filter(Resposta.autor_id == usuario_id)
        .order_by(Resposta.created_at.desc())
        .limit(50)
        .all()
    )

    return PerfilResponse(
        usuario=UsuarioPublicResponse.model_validate(usuario),
        topicos=[topico_to_response(t, db) for t in topicos],
        respostas=[resposta_to_response(r, db) for r in respostas],
    )
