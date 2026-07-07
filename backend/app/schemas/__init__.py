from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class UsuarioBase(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=6, max_length=100)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(UsuarioBase):
    id: int
    role: UserRole
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UsuarioRoleUpdate(BaseModel):
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ComunidadeCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: str = Field(default="", max_length=2000)


class ComunidadeUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=2000)


class ComunidadeResponse(BaseModel):
    id: int
    nome: str
    slug: str
    descricao: str
    criador_id: int
    criador_nome: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TopicoCreate(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    corpo: str = Field(min_length=1, max_length=10000)


class TopicoUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=200)
    corpo: str | None = Field(default=None, min_length=1, max_length=10000)


class TopicoFixarUpdate(BaseModel):
    fixado: bool


class TopicoResponse(BaseModel):
    id: int
    titulo: str
    corpo: str
    autor_id: int
    autor_nome: str | None = None
    comunidade_id: int
    comunidade_slug: str | None = None
    fixado: bool
    fechado: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RespostaCreate(BaseModel):
    corpo: str = Field(min_length=1, max_length=10000)
    parent_id: int | None = None


class RespostaUpdate(BaseModel):
    corpo: str = Field(min_length=1, max_length=10000)


class RespostaResponse(BaseModel):
    id: int
    corpo: str
    autor_id: int
    autor_nome: str | None = None
    topico_id: int
    parent_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
