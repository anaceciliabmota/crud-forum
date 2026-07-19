import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlvoTipo(str, enum.Enum):
    TOPICO = "TOPICO"
    RESPOSTA = "RESPOSTA"


class UserRole(str, enum.Enum):
    MEMBRO = "MEMBRO"
    ADMIN = "ADMIN"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.MEMBRO, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    comunidades_criadas: Mapped[list["Comunidade"]] = relationship(back_populates="criador")
    topicos: Mapped[list["Topico"]] = relationship(back_populates="autor")
    respostas: Mapped[list["Resposta"]] = relationship(back_populates="autor")
    membros_comunidade: Mapped[list["MembroComunidade"]] = relationship(back_populates="usuario")


class Comunidade(Base):
    __tablename__ = "comunidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, default="", nullable=False)
    criador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    criador: Mapped["Usuario"] = relationship(back_populates="comunidades_criadas")
    topicos: Mapped[list["Topico"]] = relationship(back_populates="comunidade", cascade="all, delete-orphan")
    membros: Mapped[list["MembroComunidade"]] = relationship(back_populates="comunidade", cascade="all, delete-orphan")


class MembroComunidade(Base):
    __tablename__ = "membros_comunidade"
    __table_args__ = (UniqueConstraint("usuario_id", "comunidade_id", name="uq_membro_comunidade"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    comunidade_id: Mapped[int] = mapped_column(ForeignKey("comunidades.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="membros_comunidade")
    comunidade: Mapped["Comunidade"] = relationship(back_populates="membros")


class Topico(Base):
    __tablename__ = "topicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    comunidade_id: Mapped[int] = mapped_column(ForeignKey("comunidades.id"), nullable=False)
    fixado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fechado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    autor: Mapped["Usuario"] = relationship(back_populates="topicos")
    comunidade: Mapped["Comunidade"] = relationship(back_populates="topicos")
    respostas: Mapped[list["Resposta"]] = relationship(back_populates="topico", cascade="all, delete-orphan")


class Resposta(Base):
    __tablename__ = "respostas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    topico_id: Mapped[int] = mapped_column(ForeignKey("topicos.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("respostas.id"), nullable=True)
    aceita: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    autor: Mapped["Usuario"] = relationship(back_populates="respostas")
    topico: Mapped["Topico"] = relationship(back_populates="respostas")
    parent: Mapped["Resposta | None"] = relationship(remote_side="Resposta.id", backref="filhas")


class Voto(Base):
    __tablename__ = "votos"
    __table_args__ = (UniqueConstraint("usuario_id", "alvo_tipo", "alvo_id", name="uq_voto_usuario_alvo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    alvo_tipo: Mapped[AlvoTipo] = mapped_column(Enum(AlvoTipo, name="alvo_tipo_enum"), nullable=False)
    alvo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    usuario: Mapped["Usuario"] = relationship()
