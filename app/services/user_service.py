# app/services/user_service.py
from __future__ import annotations

from typing import List

from structlog import get_logger

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_update import UserUpdate
from app.core.security import get_password_hash

logger = get_logger().bind(module="user_service")


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""


class UserNotFoundError(Exception):
    """Raised when a requested user cannot be found."""


class UserService:
    """
    Application service responsible for user-related business rules.

    This class acts as the orchestration layer between:
    - HTTP layer (controllers / routers);
    - persistence layer (UserRepository implementations);
    - security helpers (password hashing, etc.).

    It is also used by AuthService to fetch users during login and token
    validation flows.
    """

    def __init__(self, repo: UserRepository) -> None:
        """
        Initialize the service with a given UserRepository implementation.

        Args:
            repo: Concrete implementation of UserRepository
                  (in-memory, SQLAlchemy, etc.).
        """
        self._repo = repo

    def list_users(self) -> List[User]:
        """
        Return the full list of users from the repository.

        Returns:
            List of User models.
        """
        logger.info("Listing all users")
        users = self._repo.list_all()
        logger.debug("Users loaded", count=len(users))
        return users

    def get_user_by_username(self, username: str) -> User:
        """
        Retrieve a single user by username.

        Args:
            username: Unique username identifier.

        Raises:
            UserNotFoundError: if the user does not exist.

        Returns:
            User instance.
        """
        logger.debug("Fetching user by username", username=username)
        user = self._repo.get_by_username(username)
        if not user:
            logger.warning("User not found", username=username)
            raise UserNotFoundError(f"User '{username}' not found")
        return user

    def create_user(self, data: UserCreate) -> User:
        """
        Create a new user, ensuring uniqueness and hashing the password.

        Args:
            data: Input schema with username, full_name, password and roles.

        Raises:
            UserAlreadyExistsError: if username is already in use.

        Returns:
            Persisted User instance.
        """
        logger.debug("Creating new user", username=data.username)

        if self._repo.get_by_username(data.username):
            logger.warning("Username already exists", username=data.username)
            raise UserAlreadyExistsError(
                f"Username '{data.username}' is already in use"
            )

        user = User(
            username=data.username,
            full_name=data.full_name,
            roles=data.roles,
            hashed_password=get_password_hash(data.password),
        )

        created = self._repo.add(user)
        logger.info("User created", username=created.username)
        return created

    def delete_user(self, username: str) -> None:
        """
        Delete a user identified by username.

        Args:
            username: Unique username identifier.

        Raises:
            UserNotFoundError: if the user does not exist.
        """
        logger.debug("Deleting user", username=username)
        deleted = self._repo.delete_by_username(username)
        if not deleted:
            logger.warning("User not found for deletion", username=username)
            raise UserNotFoundError(f"User '{username}' not found")
        logger.info("User deleted", username=username)