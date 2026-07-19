from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import can_modify_content, get_current_user, get_current_user_optional
from app.models import AlvoTipo, Resposta, Topico, Usuario
from app.schemas import RespostaAceitarUpdate, RespostaCreate, RespostaResponse, RespostaUpdate, VotoInfo
from app.services.votos import contar_votos

router = APIRouter(tags=["respostas"])


def _to_response(resposta: Resposta, db: Session, usuario_id: int | None = None) -> RespostaResponse:
    votos_data = contar_votos(db, AlvoTipo.RESPOSTA, resposta.id, usuario_id)
    return RespostaResponse(
        id=resposta.id,
        corpo=resposta.corpo,
        autor_id=resposta.autor_id,
        autor_nome=resposta.autor.nome if resposta.autor else None,
        topico_id=resposta.topico_id,
        parent_id=resposta.parent_id,
        aceita=resposta.aceita,
        votos=VotoInfo(**votos_data),
        created_at=resposta.created_at,
        updated_at=resposta.updated_at,
    )


@router.get("/topicos/{topico_id}/respostas", response_model=list[RespostaResponse])
def list_respostas(
    topico_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario | None, Depends(get_current_user_optional)],
):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")

    respostas = (
        db.query(Resposta)
        .filter(Resposta.topico_id == topico_id)
        .order_by(Resposta.aceita.desc(), Resposta.created_at.asc())
        .all()
    )
    uid = current_user.id if current_user else None
    return [_to_response(r, db, uid) for r in respostas]


@router.post("/topicos/{topico_id}/respostas", response_model=RespostaResponse, status_code=status.HTTP_201_CREATED)
def create_resposta(
    topico_id: int,
    data: RespostaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    if topico.fechado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tópico fechado para respostas")

    if data.parent_id:
        parent = db.query(Resposta).filter(Resposta.id == data.parent_id, Resposta.topico_id == topico_id).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta pai não encontrada")

    resposta = Resposta(
        corpo=data.corpo,
        autor_id=current_user.id,
        topico_id=topico_id,
        parent_id=data.parent_id,
    )
    db.add(resposta)
    db.commit()
    db.refresh(resposta)
    return _to_response(resposta, db, current_user.id)


@router.put("/respostas/{resposta_id}", response_model=RespostaResponse)
def update_resposta(
    resposta_id: int,
    data: RespostaUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    resposta = db.query(Resposta).filter(Resposta.id == resposta_id).first()
    if not resposta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")
    if not can_modify_content(current_user, resposta.autor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar")

    resposta.corpo = data.corpo
    db.commit()
    db.refresh(resposta)
    return _to_response(resposta, db, current_user.id)


@router.delete("/respostas/{resposta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resposta(
    resposta_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    resposta = db.query(Resposta).filter(Resposta.id == resposta_id).first()
    if not resposta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")
    if not can_modify_content(current_user, resposta.autor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para excluir")

    db.delete(resposta)
    db.commit()


@router.patch("/respostas/{resposta_id}/aceitar", response_model=RespostaResponse)
def aceitar_resposta(
    resposta_id: int,
    data: RespostaAceitarUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    resposta = db.query(Resposta).filter(Resposta.id == resposta_id).first()
    if not resposta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")

    topico = db.query(Topico).filter(Topico.id == resposta.topico_id).first()
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")

    from app.models import UserRole
    if current_user.role != UserRole.ADMIN and current_user.id != topico.autor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Somente o autor do tópico pode marcar a melhor resposta")

    if data.aceita:
        db.query(Resposta).filter(
            Resposta.topico_id == resposta.topico_id,
            Resposta.id != resposta_id,
        ).update({"aceita": False})

    resposta.aceita = data.aceita
    db.commit()
    db.refresh(resposta)
    return _to_response(resposta, db, current_user.id)
