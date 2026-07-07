"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-07-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("MEMBRO", "ADMIN", name="userrole"), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)

    op.create_table(
        "comunidades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("criador_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["criador_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comunidades_id"), "comunidades", ["id"], unique=False)
    op.create_index(op.f("ix_comunidades_slug"), "comunidades", ["slug"], unique=True)

    op.create_table(
        "membros_comunidade",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("comunidade_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["comunidade_id"], ["comunidades.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "comunidade_id", name="uq_membro_comunidade"),
    )
    op.create_index(op.f("ix_membros_comunidade_id"), "membros_comunidade", ["id"], unique=False)

    op.create_table(
        "topicos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("corpo", sa.Text(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("comunidade_id", sa.Integer(), nullable=False),
        sa.Column("fixado", sa.Boolean(), nullable=False),
        sa.Column("fechado", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["comunidade_id"], ["comunidades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topicos_id"), "topicos", ["id"], unique=False)

    op.create_table(
        "respostas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("corpo", sa.Text(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("topico_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["respostas.id"]),
        sa.ForeignKeyConstraint(["topico_id"], ["topicos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_respostas_id"), "respostas", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_respostas_id"), table_name="respostas")
    op.drop_table("respostas")
    op.drop_index(op.f("ix_topicos_id"), table_name="topicos")
    op.drop_table("topicos")
    op.drop_index(op.f("ix_membros_comunidade_id"), table_name="membros_comunidade")
    op.drop_table("membros_comunidade")
    op.drop_index(op.f("ix_comunidades_slug"), table_name="comunidades")
    op.drop_index(op.f("ix_comunidades_id"), table_name="comunidades")
    op.drop_table("comunidades")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    op.execute("DROP TYPE IF EXISTS userrole")
