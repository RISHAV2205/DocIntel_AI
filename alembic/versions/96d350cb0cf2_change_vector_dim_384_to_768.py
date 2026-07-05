"""change_vector_dim_384_to_768

Revision ID: 96d350cb0cf2
Revises: 6cb49173145b
Create Date: 2026-07-05 15:12:33.807719

"""
from typing import Sequence, Union


import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '96d350cb0cf2'
down_revision: Union[str, Sequence[str], None] = '6cb49173145b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP INDEX IF EXISTS document_chunks_embedding_idx")

    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(768)
    """)

    op.execute("""
        CREATE INDEX document_chunks_embedding_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS document_chunks_embedding_idx")

    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(384)
    """)

    op.execute("""
        CREATE INDEX document_chunks_embedding_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
