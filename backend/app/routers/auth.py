from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import create_access_token, get_current_user
from app.models import UserRole, Usuario
from app.schemas import TokenResponse, UsuarioCreate, UsuarioLogin, UsuarioResponse
from app.services.auth import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, db: Annotated[Session, Depends(get_db)]):
    existing = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    user = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.senha),
        role=UserRole.MEMBRO,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, db: Annotated[Session, Depends(get_db)]):
    user = db.query(Usuario).filter(Usuario.email == data.email, Usuario.ativo.is_(True)).first()
    if not user or not verify_password(data.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UsuarioResponse)
def me(current_user: Annotated[Usuario, Depends(get_current_user)]):
    return current_user
