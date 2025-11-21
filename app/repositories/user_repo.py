# app/repositories/user_repo.py
"""
Abstraction for user persistence operations.

The UserRepository interface defines the contract that any user storage
implementation must satisfy (in-memory, SQLAlchemy, external service, etc.).

By coding against this abstraction instead of concrete implementations,
we keep controllers and services decoupled from the persistence details,
following the dependency inversion principle.
"""

import abc

from app.models.user import User


class UserRepository(abc.ABC):
    """
    Abstract base class representing the user repository contract.
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
    def list_all(self) -> list[User]:
        """
        Return all users stored in the underlying data source.

        Returns:
            List of User.
        """

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
    def delete_by_username(self, username: str) -> bool:
        """
        Delete a user identified by username.

        Args:
            username: Unique username.

        Returns:
            True if a user was deleted, False otherwise.
        """
