from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import can_modify_content, get_current_user, require_admin
from app.models import Comunidade, Topico, Usuario
from app.schemas import TopicoCreate, TopicoFixarUpdate, TopicoResponse, TopicoUpdate

router = APIRouter(tags=["topicos"])


def _to_response(topico: Topico) -> TopicoResponse:
    return TopicoResponse(
        id=topico.id,
        titulo=topico.titulo,
        corpo=topico.corpo,
        autor_id=topico.autor_id,
        autor_nome=topico.autor.nome if topico.autor else None,
        comunidade_id=topico.comunidade_id,
        comunidade_slug=topico.comunidade.slug if topico.comunidade else None,
        fixado=topico.fixado,
        fechado=topico.fechado,
        created_at=topico.created_at,
        updated_at=topico.updated_at,
    )


@router.get("/comunidades/{comunidade_id}/topicos", response_model=list[TopicoResponse])
def list_topicos(comunidade_id: int, db: Annotated[Session, Depends(get_db)]):
    comunidade = db.query(Comunidade).filter(Comunidade.id == comunidade_id).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")

    topicos = (
        db.query(Topico)
        .filter(Topico.comunidade_id == comunidade_id)
        .order_by(Topico.fixado.desc(), Topico.created_at.desc())
        .all()
    )
    return [_to_response(t) for t in topicos]


@router.post("/comunidades/{comunidade_id}/topicos", response_model=TopicoResponse, status_code=status.HTTP_201_CREATED)
def create_topico(
    comunidade_id: int,
    data: TopicoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comunidade = db.query(Comunidade).filter(Comunidade.id == comunidade_id).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")

    topico = Topico(
        titulo=data.titulo,
        corpo=data.corpo,
        autor_id=current_user.id,
        comunidade_id=comunidade_id,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return _to_response(topico)


@router.get("/topicos/{topico_id}", response_model=TopicoResponse)
def get_topico(topico_id: int, db: Annotated[Session, Depends(get_db)]):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    return _to_response(topico)


@router.put("/topicos/{topico_id}", response_model=TopicoResponse)
def update_topico(
    topico_id: int,
    data: TopicoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    if not can_modify_content(current_user, topico.autor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar")

    if data.titulo is not None:
        topico.titulo = data.titulo
    if data.corpo is not None:
        topico.corpo = data.corpo

    db.commit()
    db.refresh(topico)
    return _to_response(topico)


@router.delete("/topicos/{topico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topico(
    topico_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    if not can_modify_content(current_user, topico.autor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para excluir")

    db.delete(topico)
    db.commit()


@router.patch("/topicos/{topico_id}/fixar", response_model=TopicoResponse)
def fixar_topico(
    topico_id: int,
    data: TopicoFixarUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_admin)],
):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")

    topico.fixado = data.fixado
    db.commit()
    db.refresh(topico)
    return _to_response(topico)
