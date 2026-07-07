from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin
from app.models import Usuario
from app.schemas import UsuarioResponse, UsuarioRoleUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/usuarios", response_model=list[UsuarioResponse])
def list_usuarios(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_admin)],
):
    return db.query(Usuario).order_by(Usuario.created_at.desc()).all()


@router.patch("/usuarios/{usuario_id}/role", response_model=UsuarioResponse)
def update_usuario_role(
    usuario_id: int,
    data: UsuarioRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(require_admin)],
):
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
