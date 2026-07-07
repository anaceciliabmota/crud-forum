from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import UserRole, Usuario

security = HTTPBearer(auto_error=False)


def create_access_token(user_id: int, role: UserRole) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "role": role.value, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario | None:
    if credentials is None:
        return None
    return _get_user_from_token(credentials.credentials, db)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação necessária")
    user = _get_user_from_token(credentials.credentials, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return user


def require_admin(current_user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    return current_user


def _get_user_from_token(token: str, db: Session) -> Usuario | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub", 0))
    except (JWTError, ValueError):
        return None
    user = db.query(Usuario).filter(Usuario.id == user_id, Usuario.ativo.is_(True)).first()
    return user


def can_modify_content(user: Usuario, autor_id: int) -> bool:
    return user.role == UserRole.ADMIN or user.id == autor_id


def can_modify_comunidade(user: Usuario, criador_id: int) -> bool:
    return user.role == UserRole.ADMIN or user.id == criador_id
