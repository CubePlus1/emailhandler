"""SQLAlchemy models for email handler."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Mailbox(Base):
    """Mailbox account model."""

    __tablename__ = "mailboxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    emails: Mapped[List["Email"]] = relationship(
        "Email", back_populates="mailbox", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Mailbox(id={self.id}, email='{self.email}')>"


class Email(Base):
    """Email message model."""

    __tablename__ = "emails"
    __table_args__ = (
        Index("idx_emails_mailbox", "mailbox_id"),
        Index("idx_emails_folder", "folder"),
        Index("idx_emails_received", "received_at", postgresql_ops={"received_at": "DESC"}),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mailboxes.id"), nullable=False
    )
    message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_address: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    html_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    folder: Mapped[str] = mapped_column(String(50), default="inbox", nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    verification_link: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True
    )  # Legacy compatibility
    raw_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    mailbox: Mapped["Mailbox"] = relationship("Mailbox", back_populates="emails")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="email", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, message_id='{self.message_id}', subject='{self.subject}')>"


class Attachment(Base):
    """Email attachment model."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emails.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, filename='{self.filename}', size={self.size})>"
