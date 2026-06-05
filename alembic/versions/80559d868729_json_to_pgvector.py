"""json_to_pgvector

Revision ID: 80559d868729
Revises: ecd67fab8250
Create Date: 2026-06-05 18:15:35.830138

"""
from typing import Sequence, Union
from pgvector.sqlalchemy import Vector
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80559d868729'
down_revision: Union[str, Sequence[str], None] = 'ecd67fab8250'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # enable pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # add new vector column
    op.add_column(
        "document_chunks",
        sa.Column("embedding_new", Vector(384), nullable=True)
    )

    # migrate existing json data to vector
    op.execute("""
        UPDATE document_chunks
        SET embedding_new = embedding::text::vector
        WHERE embedding IS NOT NULL
    """)

    # drop old json column
    op.drop_column("document_chunks", "embedding")

    # rename new column
    op.alter_column(
        "document_chunks",
        "embedding_new",
        new_column_name="embedding"
    )

    # add HNSW index
    op.execute("""
        CREATE INDEX document_chunks_embedding_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS document_chunks_embedding_idx")
    op.add_column(
        "document_chunks",
        sa.Column("embedding_old", sa.JSON, nullable=True)
    )
    op.execute("""
        UPDATE document_chunks
        SET embedding_old = embedding::text::json
    """)
    op.drop_column("document_chunks", "embedding")
    op.alter_column(
        "document_chunks",
        "embedding_old",
        new_column_name="embedding"
    )