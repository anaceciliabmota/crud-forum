from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import can_modify_comunidade, get_current_user, get_current_user_optional, require_admin
from app.models import Comunidade, MembroComunidade, Usuario
from app.schemas import ComunidadeCreate, ComunidadeResponse, ComunidadeUpdate
from app.services.slug import slugify

router = APIRouter(prefix="/comunidades", tags=["comunidades"])


def _to_response(comunidade: Comunidade, db: Session | None = None, usuario_id: int | None = None) -> ComunidadeResponse:
    eh_membro = False
    if db is not None and usuario_id is not None:
        eh_membro = (
            db.query(MembroComunidade)
            .filter(
                MembroComunidade.usuario_id == usuario_id,
                MembroComunidade.comunidade_id == comunidade.id,
            )
            .first()
        ) is not None
    return ComunidadeResponse(
        id=comunidade.id,
        nome=comunidade.nome,
        slug=comunidade.slug,
        descricao=comunidade.descricao,
        criador_id=comunidade.criador_id,
        criador_nome=comunidade.criador.nome if comunidade.criador else None,
        eh_membro=eh_membro,
        created_at=comunidade.created_at,
    )


@router.get("", response_model=list[ComunidadeResponse])
def list_comunidades(db: Annotated[Session, Depends(get_db)]):
    comunidades = db.query(Comunidade).order_by(Comunidade.created_at.desc()).all()
    return [_to_response(c) for c in comunidades]


@router.post("", response_model=ComunidadeResponse, status_code=status.HTTP_201_CREATED)
def create_comunidade(
    data: ComunidadeCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    base_slug = slugify(data.nome)
    slug = base_slug
    counter = 1
    while db.query(Comunidade).filter(Comunidade.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    comunidade = Comunidade(
        nome=data.nome,
        slug=slug,
        descricao=data.descricao,
        criador_id=current_user.id,
    )
    db.add(comunidade)
    db.flush()

    membro = MembroComunidade(usuario_id=current_user.id, comunidade_id=comunidade.id)
    db.add(membro)
    db.commit()
    db.refresh(comunidade)
    return _to_response(comunidade)


@router.get("/{slug}", response_model=ComunidadeResponse)
def get_comunidade(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario | None, Depends(get_current_user_optional)] = None,
):
    comunidade = db.query(Comunidade).filter(Comunidade.slug == slug).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")
    return _to_response(comunidade, db=db, usuario_id=current_user.id if current_user else None)


@router.put("/{comunidade_id}", response_model=ComunidadeResponse)
def update_comunidade(
    comunidade_id: int,
    data: ComunidadeUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comunidade = db.query(Comunidade).filter(Comunidade.id == comunidade_id).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")
    if not can_modify_comunidade(current_user, comunidade.criador_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar")

    if data.nome is not None:
        comunidade.nome = data.nome
    if data.descricao is not None:
        comunidade.descricao = data.descricao

    db.commit()
    db.refresh(comunidade)
    return _to_response(comunidade)


@router.delete("/{comunidade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comunidade(
    comunidade_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_admin)],
):
    comunidade = db.query(Comunidade).filter(Comunidade.id == comunidade_id).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")
    db.delete(comunidade)
    db.commit()


@router.post("/{comunidade_id}/entrar", status_code=status.HTTP_201_CREATED)
def entrar_comunidade(
    comunidade_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    comunidade = db.query(Comunidade).filter(Comunidade.id == comunidade_id).first()
    if not comunidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunidade não encontrada")

    existing = (
        db.query(MembroComunidade)
        .filter(
            MembroComunidade.usuario_id == current_user.id,
            MembroComunidade.comunidade_id == comunidade_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já é membro desta comunidade")

    membro = MembroComunidade(usuario_id=current_user.id, comunidade_id=comunidade_id)
    db.add(membro)
    db.commit()
    return {"detail": "Entrou na comunidade"}

@router.delete("/{comunidade_id}/sair", status_code=status.HTTP_204_NO_CONTENT)
def sair_comunidade(
    comunidade_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    membro = (
        db.query(MembroComunidade)
        .filter(
            MembroComunidade.usuario_id == current_user.id,
            MembroComunidade.comunidade_id == comunidade_id,
        )
        .first()
    )
    if not membro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não é membro desta comunidade")
    db.delete(membro)
    db.commit()
