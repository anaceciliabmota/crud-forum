from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Comunidade, Topico
from app.routers.comunidades import _to_response as comunidade_to_response
from app.routers.topicos import _to_response as topico_to_response
from app.schemas import BuscaResponse

router = APIRouter(tags=["busca"])


@router.get("/busca", response_model=BuscaResponse)
def buscar(
    q: Annotated[str, Query(min_length=2, max_length=100)],
    db: Annotated[Session, Depends(get_db)],
):
    padrao = f"%{q}%"

    comunidades = (
        db.query(Comunidade)
        .filter(Comunidade.nome.ilike(padrao))
        .order_by(Comunidade.created_at.desc())
        .limit(20)
        .all()
    )
    topicos = (
        db.query(Topico)
        .filter(Topico.titulo.ilike(padrao))
        .order_by(Topico.created_at.desc())
        .limit(20)
        .all()
    )

    return BuscaResponse(
        comunidades=[comunidade_to_response(c) for c in comunidades],
        topicos=[topico_to_response(t, db) for t in topicos],
    )
