# app/infra/repositories/sqlalchemy/user_repo_sqlalchemy.py
from __future__ import annotations

from typing import List, Optional

from structlog import get_logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.tables.user_table import UserTable
from app.models.user import User
from app.repositories.user_repo import UserRepository

logger = get_logger().bind(module="user_repo_sqlalchemy")


class UserRepoSQLAlchemy(UserRepository):
    """
    SQLAlchemy-based implementation of UserRepository.

    This repository converts between:
    - SQLAlchemy ORM entities (UserTable)
    - Pydantic schemas used by the service layer (User)
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a DB session.

        Args:
            db: SQLAlchemy Session, usually injected via FastAPI dependency.
        """
        self._db = db

    # ---------- Internal helpers ----------

    @staticmethod
    def _to_schema(row: UserTable) -> User:
        """
        Convert a UserTable ORM instance to User schema.

        Note:
            At the moment User does not carry the `id` field;
            we only map the fields needed by the application layer.
        """
        roles = [r.strip() for r in (row.roles or "").split(",") if r.strip()]
        return User(
            username=row.username,
            full_name=row.full_name,
            hashed_password=row.hashed_password,
            roles=roles,
        )

    # ---------- Public API (UserRepository) ----------

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username from the database.

        Args:
            username: Unique username.

        Returns:
            User if found, or None otherwise.
        """
        logger.debug("Fetching user from DB", username=username)
        stmt = select(UserTable).where(UserTable.username == username)
        row: UserTable | None = self._db.execute(stmt).scalar_one_or_none()

        if row is None:
            logger.info("User not found in DB", username=username)
            return None

        return self._to_schema(row)

    def list_all(self) -> List[User]:
        """
        Return all users stored in the database.

        Returns:
            List[User]
        """
        logger.debug("Listing all users from DB")
        stmt = select(UserTable)
        rows = self._db.execute(stmt).scalars().all()
        users = [self._to_schema(row) for row in rows]
        logger.info("Users loaded from DB", count=len(users))
        return users

    def add(self, user: User) -> User:
        """
        Persist a new user into the database.

        Args:
            user: User instance with already hashed password.

        Returns:
            User (same data, already persisted).
        """
        logger.debug("Persisting new user to DB", username=user.username)
        roles_str = ",".join(user.roles)

        row = UserTable(
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            roles=roles_str,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        logger.info("User persisted to DB", username=user.username, id=row.id)
        return user

    def delete_by_username(self, username: str) -> bool:
        """
        Delete a user from the database by username.

        Args:
            username: Unique username to be deleted.

        Returns:
            True if a row was deleted, False otherwise.
        """
        logger.debug("Deleting user from DB", username=username)
        stmt = select(UserTable).where(UserTable.username == username)
        row: UserTable | None = self._db.execute(stmt).scalar_one_or_none()

        if row is None:
            logger.info("User not found in DB for deletion", username=username)
            return False

        self._db.delete(row)
        self._db.commit()
        logger.info("User deleted from DB", username=username, id=row.id)
        return True
