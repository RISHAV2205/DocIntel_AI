"""fix_pgvector

Revision ID: 6cb49173145b
Revises: 80559d868729
Create Date: 2026-06-06 11:18:06.838100

"""
from typing import Sequence, Union
from pgvector.sqlalchemy import Vector
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb49173145b'
down_revision: Union[str, Sequence[str], None] = '80559d868729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.drop_column("document_chunks", "embedding")

    op.add_column(
        "document_chunks",
        sa.Column("embedding", Vector(384), nullable=True)
    )

    op.execute("""
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
    """)


def downgrade():
    op.execute("""
        DROP INDEX IF EXISTS document_chunks_embedding_idx
    """)

    op.drop_column("document_chunks", "embedding")

    op.add_column(
        "document_chunks",
        sa.Column("embedding", sa.JSON(), nullable=True)
    )
