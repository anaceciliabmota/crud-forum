from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import AlvoTipo, Resposta, Topico, Usuario, Voto
from app.schemas import VotoCreate, VotoInfo
from app.services.votos import contar_votos

router = APIRouter(prefix="/votos", tags=["votos"])


def _validar_alvo(db: Session, alvo_tipo: str, alvo_id: int):
    if alvo_tipo == AlvoTipo.TOPICO:
        obj = db.query(Topico).filter(Topico.id == alvo_id).first()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
        return obj
    else:
        obj = db.query(Resposta).filter(Resposta.id == alvo_id).first()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")
        return obj


@router.post("", response_model=VotoInfo, status_code=status.HTTP_201_CREATED)
def votar(
    data: VotoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    if data.valor == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valor do voto deve ser +1 ou -1")

    alvo_tipo = AlvoTipo(data.alvo_tipo)
    alvo = _validar_alvo(db, alvo_tipo, data.alvo_id)

    # não votar no próprio conteúdo
    autor_id = alvo.autor_id
    if autor_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode votar no próprio conteúdo")

    voto = (
        db.query(Voto)
        .filter(
            Voto.usuario_id == current_user.id,
            Voto.alvo_tipo == alvo_tipo,
            Voto.alvo_id == data.alvo_id,
        )
        .first()
    )

    if voto:
        voto.valor = data.valor
    else:
        voto = Voto(
            usuario_id=current_user.id,
            alvo_tipo=alvo_tipo,
            alvo_id=data.alvo_id,
            valor=data.valor,
        )
        db.add(voto)

    db.commit()
    return VotoInfo(**contar_votos(db, alvo_tipo, data.alvo_id, current_user.id))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def remover_voto(
    alvo_tipo: Annotated[str, Query(pattern="^(TOPICO|RESPOSTA)$")],
    alvo_id: Annotated[int, Query()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    tipo = AlvoTipo(alvo_tipo)
    voto = (
        db.query(Voto)
        .filter(
            Voto.usuario_id == current_user.id,
            Voto.alvo_tipo == tipo,
            Voto.alvo_id == alvo_id,
        )
        .first()
    )
    if not voto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado")

    db.delete(voto)
    db.commit()
