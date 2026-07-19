"""features v2: coluna aceita em respostas + tabela votos

Revision ID: 002
Revises: 001
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("respostas", sa.Column("aceita", sa.Boolean(), nullable=False, server_default="false"))

    op.create_table(
        "votos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("alvo_tipo", sa.Enum("TOPICO", "RESPOSTA", name="alvo_tipo_enum"), nullable=False),
        sa.Column("alvo_id", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "alvo_tipo", "alvo_id", name="uq_voto_usuario_alvo"),
    )
    op.create_index(op.f("ix_votos_id"), "votos", ["id"], unique=False)
    op.create_index("ix_votos_alvo", "votos", ["alvo_tipo", "alvo_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_votos_alvo", table_name="votos")
    op.drop_index(op.f("ix_votos_id"), table_name="votos")
    op.drop_table("votos")
    op.execute("DROP TYPE IF EXISTS alvo_tipo_enum")
    op.drop_column("respostas", "aceita")
