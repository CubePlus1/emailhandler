"""Initial migration with FTS5 support

Revision ID: 001
Revises:
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create mailboxes table
    op.create_table('mailboxes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create emails table
    op.create_table('emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mailbox_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('from_address', sa.String(length=255), nullable=False),
        sa.Column('to_address', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('html_body', sa.Text(), nullable=True),
        sa.Column('text_body', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_starred', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('folder', sa.String(length=50), nullable=False, server_default='inbox'),
        sa.Column('received_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('verification_link', sa.String(length=1000), nullable=True),
        sa.Column('raw_headers', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['mailbox_id'], ['mailboxes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    op.create_index('idx_emails_mailbox', 'emails', ['mailbox_id'], unique=False)
    op.create_index('idx_emails_folder', 'emails', ['folder'], unique=False)
    op.create_index('idx_emails_received', 'emails', ['received_at'], unique=False)

    # Create attachments table
    op.create_table('attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create full-text search support based on database type
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'sqlite':
        # SQLite: Use FTS5 virtual table
        op.execute("""
            CREATE VIRTUAL TABLE emails_fts USING fts5(
                subject,
                from_address,
                to_address,
                text_body,
                content='emails',
                content_rowid='id'
            )
        """)

        # Create triggers to keep FTS5 table in sync
        op.execute("""
            CREATE TRIGGER emails_ai AFTER INSERT ON emails BEGIN
                INSERT INTO emails_fts(rowid, subject, from_address, to_address, text_body)
                VALUES (new.id, new.subject, new.from_address, new.to_address, new.text_body);
            END
        """)

        op.execute("""
            CREATE TRIGGER emails_ad AFTER DELETE ON emails BEGIN
                INSERT INTO emails_fts(emails_fts, rowid, subject, from_address, to_address, text_body)
                VALUES('delete', old.id, old.subject, old.from_address, old.to_address, old.text_body);
            END
        """)

        op.execute("""
            CREATE TRIGGER emails_au AFTER UPDATE ON emails BEGIN
                INSERT INTO emails_fts(emails_fts, rowid, subject, from_address, to_address, text_body)
                VALUES('delete', old.id, old.subject, old.from_address, old.to_address, old.text_body);
                INSERT INTO emails_fts(rowid, subject, from_address, to_address, text_body)
                VALUES (new.id, new.subject, new.from_address, new.to_address, new.text_body);
            END
        """)

    elif dialect == 'postgresql':
        # PostgreSQL: Use tsvector and GIN index
        # Add tsvector column for full-text search
        op.add_column('emails', sa.Column('search_vector', sa.dialects.postgresql.TSVECTOR(), nullable=True))

        # Create GIN index for fast full-text search
        op.execute("""
            CREATE INDEX idx_emails_search_vector ON emails USING GIN(search_vector)
        """)

        # Create function to update search vector
        op.execute("""
            CREATE OR REPLACE FUNCTION emails_search_vector_update() RETURNS trigger AS $$
            BEGIN
                NEW.search_vector :=
                    setweight(to_tsvector('english', COALESCE(NEW.subject, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(NEW.from_address, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(NEW.to_address, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(NEW.text_body, '')), 'C');
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """)

        # Create trigger to auto-update search vector
        op.execute("""
            CREATE TRIGGER emails_search_vector_trigger
            BEFORE INSERT OR UPDATE ON emails
            FOR EACH ROW
            EXECUTE FUNCTION emails_search_vector_update();
        """)

        # Update existing rows (if any)
        op.execute("""
            UPDATE emails SET search_vector =
                setweight(to_tsvector('english', COALESCE(subject, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(from_address, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(to_address, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(text_body, '')), 'C')
        """)


def downgrade() -> None:
    # Drop full-text search based on database type
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'sqlite':
        # Drop FTS5 triggers
        op.execute("DROP TRIGGER IF EXISTS emails_au")
        op.execute("DROP TRIGGER IF EXISTS emails_ad")
        op.execute("DROP TRIGGER IF EXISTS emails_ai")

        # Drop FTS5 virtual table
        op.execute("DROP TABLE IF EXISTS emails_fts")

    elif dialect == 'postgresql':
        # Drop PostgreSQL full-text search
        op.execute("DROP TRIGGER IF EXISTS emails_search_vector_trigger ON emails")
        op.execute("DROP FUNCTION IF EXISTS emails_search_vector_update()")
        op.execute("DROP INDEX IF EXISTS idx_emails_search_vector")
        op.drop_column('emails', 'search_vector')

    # Drop regular tables
    op.drop_table('attachments')

    op.drop_index('idx_emails_received', table_name='emails')
    op.drop_index('idx_emails_folder', table_name='emails')
    op.drop_index('idx_emails_mailbox', table_name='emails')
    op.drop_table('emails')

    op.drop_table('mailboxes')
