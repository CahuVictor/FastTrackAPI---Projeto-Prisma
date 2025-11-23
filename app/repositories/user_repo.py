# app/repositories/user_repo.py
"""
Abstraction for user persistence operations.

The UserRepository interface defines the contract that any user storage
implementation must satisfy (in-memory, SQLAlchemy, external service, etc.).

By coding against this abstraction instead of concrete implementations,
we keep controllers and services decoupled from the persistence details,
following the dependency inversion principle.
"""
from __future__ import annotations

import abc
from datetime import datetime
from typing import List

from app.models.user import User


class UserRepository(abc.ABC):
    """
    Abstraction for user persistence operations.

    Concrete implementations (in-memory, SQLAlchemy, external service, etc.)
    must implement this interface, allowing services to remain decoupled
    from storage details.
    """

    # ---------------- CRUD core ---------------- #

    @abc.abstractmethod
    def add(self, user: User) -> User:
        """
        Persist a new user (or update an existing one, depending on implementation).

        Args:
            user: User instance to be persisted.

        Returns:
            Persisted User instance.
        """

    @abc.abstractmethod
    def get(self, user_id: int) -> User | None:
        """
        Retrieve a user by its internal ID.

        Returns:
            User instance or None if not found.
        """
        
    @abc.abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by its username.

        Args:
            username: Unique username.

        Returns:
            User or None if not found.
        """
    
    @abc.abstractmethod
    def update(self, user: User) -> User:
        """
        Update an existing user in the underlying storage.

        The user must have a valid ID.
        """
    
    @abc.abstractmethod
    def delete_by_username(self, username: str) -> bool:
        """
        Delete a user identified by username.

        Args:
            username: Unique username.

        Returns:
            True if a user was deleted, False otherwise.
        """
    
    # ---------------- Queries ---------------- #

    @abc.abstractmethod
    def list_all(self) -> list[User]:
        """
        Return all users stored in the underlying data source.

        Returns:
            List of User.
        """

    @abc.abstractmethod
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        username: str | None = None,
        fullname: str | None = None,
        roles: list[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        **filters,
    ) -> List[User]:
        """
        List users with optional filters and pagination.

        Implementations may ignore unknown filters, but they should
        at least honor the core arguments defined here.
        """