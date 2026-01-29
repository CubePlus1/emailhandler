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
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('imap_host', sa.String(), nullable=False),
        sa.Column('imap_port', sa.Integer(), nullable=False),
        sa.Column('imap_username', sa.String(), nullable=False),
        sa.Column('imap_password', sa.String(), nullable=False),
        sa.Column('smtp_host', sa.String(), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True),
        sa.Column('smtp_username', sa.String(), nullable=True),
        sa.Column('smtp_password', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mailboxes_id'), 'mailboxes', ['id'], unique=False)
    op.create_index(op.f('ix_mailboxes_name'), 'mailboxes', ['name'], unique=True)

    # Create emails table
    op.create_table('emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mailbox_id', sa.Integer(), nullable=False),
        sa.Column('uid', sa.String(), nullable=False),
        sa.Column('folder', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=True),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('sender', sa.String(), nullable=True),
        sa.Column('recipient', sa.String(), nullable=True),
        sa.Column('cc', sa.String(), nullable=True),
        sa.Column('bcc', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('html_body', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=True),
        sa.Column('flags', sa.String(), nullable=True),
        sa.Column('raw_headers', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['mailbox_id'], ['mailboxes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mailbox_id', 'uid', 'folder', name='_mailbox_uid_folder_uc')
    )
    op.create_index(op.f('ix_emails_id'), 'emails', ['id'], unique=False)
    op.create_index('idx_emails_mailbox', 'emails', ['mailbox_id'], unique=False)
    op.create_index('idx_emails_folder', 'emails', ['folder'], unique=False)
    op.create_index('idx_emails_received', 'emails', ['received_at'], unique=False)

    # Create attachments table
    op.create_table('attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('content', sa.LargeBinary(), nullable=True),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attachments_id'), 'attachments', ['id'], unique=False)

    # Create FTS5 virtual table for emails
    op.execute("""
        CREATE VIRTUAL TABLE emails_fts USING fts5(
            subject,
            sender,
            recipient,
            body,
            content='emails',
            content_rowid='id'
        )
    """)

    # Create triggers to keep FTS5 table in sync
    op.execute("""
        CREATE TRIGGER emails_ai AFTER INSERT ON emails BEGIN
            INSERT INTO emails_fts(rowid, subject, sender, recipient, body)
            VALUES (new.id, new.subject, new.sender, new.recipient, new.body);
        END
    """)

    op.execute("""
        CREATE TRIGGER emails_ad AFTER DELETE ON emails BEGIN
            INSERT INTO emails_fts(emails_fts, rowid, subject, sender, recipient, body)
            VALUES('delete', old.id, old.subject, old.sender, old.recipient, old.body);
        END
    """)

    op.execute("""
        CREATE TRIGGER emails_au AFTER UPDATE ON emails BEGIN
            INSERT INTO emails_fts(emails_fts, rowid, subject, sender, recipient, body)
            VALUES('delete', old.id, old.subject, old.sender, old.recipient, old.body);
            INSERT INTO emails_fts(rowid, subject, sender, recipient, body)
            VALUES (new.id, new.subject, new.sender, new.recipient, new.body);
        END
    """)


def downgrade() -> None:
    # Drop FTS5 triggers
    op.execute("DROP TRIGGER IF EXISTS emails_au")
    op.execute("DROP TRIGGER IF EXISTS emails_ad")
    op.execute("DROP TRIGGER IF EXISTS emails_ai")

    # Drop FTS5 virtual table
    op.execute("DROP TABLE IF EXISTS emails_fts")

    # Drop regular tables
    op.drop_index(op.f('ix_attachments_id'), table_name='attachments')
    op.drop_table('attachments')

    op.drop_index('idx_emails_received', table_name='emails')
    op.drop_index('idx_emails_folder', table_name='emails')
    op.drop_index('idx_emails_mailbox', table_name='emails')
    op.drop_index(op.f('ix_emails_id'), table_name='emails')
    op.drop_table('emails')

    op.drop_index(op.f('ix_mailboxes_name'), table_name='mailboxes')
    op.drop_index(op.f('ix_mailboxes_id'), table_name='mailboxes')
    op.drop_table('mailboxes')
