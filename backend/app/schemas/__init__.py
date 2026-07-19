from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class VotoInfo(BaseModel):
    upvotes: int
    downvotes: int
    score: int
    meu_voto: int | None = None


class VotoCreate(BaseModel):
    alvo_tipo: str = Field(pattern="^(TOPICO|RESPOSTA)$")
    alvo_id: int
    valor: int = Field(ge=-1, le=1)


class VotoDelete(BaseModel):
    alvo_tipo: str = Field(pattern="^(TOPICO|RESPOSTA)$")
    alvo_id: int


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


class UsuarioPublicResponse(BaseModel):
    id: int
    nome: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


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
    eh_membro: bool = False
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
    votos: VotoInfo = VotoInfo(upvotes=0, downvotes=0, score=0)
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
    aceita: bool
    votos: VotoInfo = VotoInfo(upvotes=0, downvotes=0, score=0)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RespostaAceitarUpdate(BaseModel):
    aceita: bool


class PerfilResponse(BaseModel):
    usuario: UsuarioPublicResponse
    topicos: list[TopicoResponse]
    respostas: list[RespostaResponse]


class BuscaResponse(BaseModel):
    comunidades: list[ComunidadeResponse]
    topicos: list[TopicoResponse]
