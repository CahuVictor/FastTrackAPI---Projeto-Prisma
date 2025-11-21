# app/models/user_table.py
"""
SQLAlchemy ORM mapping for the `users` table.

This table represents how users are persisted in the relational database.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.infra.db.base import Base


class UserTable(Base):
    """
    SQLAlchemy model for the `users` table.

    Fields:
        id: Primary key (auto-increment).
        username: Unique username, used as business identifier.
        full_name: Optional full name for display purposes.
        hashed_password: Password already hashed (never store raw passwords).
        roles: Comma-separated list of roles (to be mapped by service/repo).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(
        String,
        nullable=False,
        comment="Comma-separated roles. Example: 'admin,editor'",
    )
    
    # Audit fields (who did what/when)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
