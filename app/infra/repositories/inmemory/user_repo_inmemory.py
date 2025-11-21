# app/repositories/user_repo_inmemory.py
"""
In-memory implementation of UserRepository.

This repository is mainly used for:
- local development;
- fast tests (when ENVIRONMENT=test.inmemory);
- demo environments without a real database.

The data is stored in a simple Python dict (process-local, non-persistent).
"""
from __future__ import annotations

from datetime import datetime
from typing import List
from structlog import get_logger

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.security import get_password_hash

logger = get_logger().bind(module="user_repo_mem")


class UserRepoInMemory(): # UserRepository):
    """
    Simple in-memory user repository.

    All data is initialized in the constructor using a small predefined
    list of demo users (_RAW_USERS). This is intentionally *not* thread-safe,
    but it is sufficient for unit tests and local development.

    Internal structure:
        - _storage: maps user_id (int) -> User
        - _username_index: maps username (str) -> user_id (int)
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory storage with a fixed set of demo users.

        Note:
            Passwords are hashed at startup to simulate a real environment
            without the cost of hashing on every request.
        """
        _RAW_USERS = [
            # username  full name           password      roles
            ("alice", "Alice Liddell", "secret123", ["admin"]),
            ("bob", "Bob Builder", "builder123", ["editor"]),
            ("carol", "Carol Jones", "pass123", ["viewer"]),
            ("dave", "Dave Stone", "pass123", ["viewer"]),
            ("eve", "Eve Adams", "pass123", ["editor"]),
            ("frank", "Frank Wright", "pass123", ["editor"]),
            ("grace", "Grace Kim", "pass123", ["viewer"]),
            ("heidi", "Heidi Cruz", "pass123", ["viewer"]),
            ("ivan", "Ivan Lee", "pass123", ["viewer"]),
            ("judy", "Judy Moe", "pass123", ["viewer"]),
        ]

        # Próximo ID incremental que será atribuído a novos usuários.
        self._next_id: int = 1

        # Armazena os usuários em memória, indexados por ID.
        self._storage: dict[int, User] = {}

        # Índice auxiliar para buscar rapidamente por username.
        self._username_index: dict[str, int] = {}

        now = datetime.utcnow()

        # Inicializa usuários de exemplo com id, created_at e updated_at.
        for username, fullname, raw_pwd, roles in _RAW_USERS:
            user_id = self._generate_id()
            user = User(
                id=user_id,
                username=username,
                full_name=fullname,
                hashed_password=get_password_hash(raw_pwd),
                roles=roles,
                created_at=now,
                updated_at=now,
            )
            self._storage[user_id] = user
            self._username_index[username] = user_id

        logger.info(
            "In-memory user repository initialized",
            total_users=len(self._storage),
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _generate_id(self) -> int:
        """
        Generate a new incremental ID for in-memory users.

        Returns:
            New integer ID.
        """
        new_id = self._next_id
        self._next_id += 1
        return new_id


    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def add(self, user: User) -> User:
        """
        Add or replace a user in the in-memory store.

        If the user has no ID, a new one is generated.
        Audit fields (created_at, updated_at) are also handled here.

        Args:
            user: User instance.

        Returns:
            The persisted User instance (with id and audit fields set).
        """
        if user.id is None:
            user.id = self._generate_id()

        now = datetime.utcnow()

        # Se created_at não vier preenchido, assume agora.
        if user.created_at is None:
            user.created_at = now

        # Sempre atualiza o updated_at na escrita.
        user.updated_at = now

        # Atualiza os índices internos.
        self._storage[user.id] = user
        self._username_index[user.username] = user.id

        logger.info(
            "Adding new in-memory user",
            user_id=user.id,
            username=user.username,
            roles=user.roles,
        )

        return user


    # ------------------------------------------------------------------ #
    # READ (por username) - requerido pelo UserRepository
    # ------------------------------------------------------------------ #
    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username from the in-memory storage.

        Args:
            username: Unique username.

        Returns:
            User or None.
        """
        user_id = self._username_index.get(username)
        if user_id is None:
            logger.info("User not found in memory by username", username=username)
            return None

        user = self._storage.get(user_id)
        if user:
            logger.debug(
                "Fetching in-memory user",
                user_id=user.id,
                username=user.username,
                roles=user.roles,
            )
        else:
            logger.warning(
                "Username index points to missing user_id",
                username=username,
                user_id=user_id,
            )
            
        return user

    # ------------------------------------------------------------------ #
    # READ (por ID) - novo método
    # ------------------------------------------------------------------ #
    def get(self, user_id: int) -> User | None:
        """
        Retrieve a user by its internal ID.

        Args:
            user_id: Internal numeric identifier.

        Returns:
            User or None.
        """
        user = self._storage.get(user_id)
        if user:
            logger.debug(
                "Fetching in-memory user by ID",
                user_id=user.id,
                username=user.username,
                roles=user.roles,
            )
        else:
            logger.info("User not found in memory by ID", user_id=user_id)
        return user

    # ------------------------------------------------------------------ #
    # LIST (simples) - requerido pelo UserRepository
    # ------------------------------------------------------------------ #
    def list_all(self) -> List[User]:
        """
        Return all users stored in memory.

        Returns:
            List[User]
        """
        users = list(self._storage.values())

        logger.info(
            "Listing all in-memory users",
            total=len(users),
        )

        return users

    # ------------------------------------------------------------------ #
    # LIST (filtrada/paginada) - novo método
    # ------------------------------------------------------------------ #
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

        This is a higher-level query API that can be used by services
        that need more control over filtering than `list_all()`.

        Args:
            skip: Number of items to skip (for pagination).
            limit: Maximum number of items to return.
            username: If provided, filters by exact username.
            fullname: If provided, filters by exact full_name.
            roles: If provided, only users that have *at least* these roles
                   (i.e., roles ? user.roles) are returned.
            created_at: If provided, filters by exact creation timestamp.
            updated_at: If provided, filters by exact updated timestamp.
            **filters: Extra filters (currently ignored, but accepted to keep
                       the signature extensible).

        Returns:
            Filtered list of User instances.
        """
        users = list(self._storage.values())

        # Filtro por username (exato)
        if username is not None:
            users = [u for u in users if u.username == username]

        # Filtro por full_name (exato)
        if fullname is not None:
            users = [u for u in users if u.full_name == fullname]

        # Filtro por roles (subset)
        if roles is not None:
            roles_set = set(roles)
            users = [u for u in users if roles_set.issubset(set(u.roles))]

        # Filtro por created_at (igualdade simples)
        if created_at is not None:
            users = [u for u in users if u.created_at == created_at]

        # Filtro por updated_at (igualdade simples)
        if updated_at is not None:
            users = [u for u in users if u.updated_at == updated_at]

        # No momento, filtros extras são apenas logados (não aplicados).
        if filters:
            logger.debug(
                "Additional filters received (not applied in memory repo)",
                filters=filters,
            )

        # Paginação simples em memória.
        if skip < 0:
            skip = 0
        if limit is None or limit < 0:
            # Se limit não fizer sentido, retorna tudo a partir de skip.
            paginated = users[skip:]
        else:
            paginated = users[skip : skip + limit]

        logger.info(
            "Listing in-memory users with filters",
            total=len(users),
            returned=len(paginated),
            skip=skip,
            limit=limit,
        )

        return paginated

    # ------------------------------------------------------------------ #
    # UPDATE - novo método
    # ------------------------------------------------------------------ #
    def update(self, user: User) -> User:
        """
        Update an existing user in the in-memory store.

        The user must have a valid ID. If the username changes,
        the username index is updated accordingly.

        Args:
            user: Updated User entity.

        Raises:
            ValueError: If user.id is None.
            KeyError: If no user exists with this ID.

        Returns:
            The updated User instance.
        """
        if user.id is None:
            raise ValueError("Cannot update user without an 'id'")

        existing = self._storage.get(user.id)
        if existing is None:
            raise KeyError(f"User with id={user.id} not found for update")

        # Preserve created_at if it is not explicitly set.
        if user.created_at is None:
            user.created_at = existing.created_at

        # Always update updated_at.
        user.updated_at = datetime.utcnow()

        # Se o username mudou, ajusta o índice.
        old_username = existing.username
        if old_username != user.username:
            self._username_index.pop(old_username, None)

        self._storage[user.id] = user
        self._username_index[user.username] = user.id

        logger.info(
            "Updated in-memory user",
            user_id=user.id,
            username=user.username,
            roles=user.roles,
        )

        return user

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def delete_by_username(self, username: str) -> bool:
        """
        Delete a user by username from the in-memory store.

        Args:
            username: Unique username.

        Returns:
            True if deleted, False otherwise.
        """
        if username in self._storage:
            logger.info("Removing in-memory user", user_id=user.id, username=username)
            del self._storage[username]
            return True

        logger.warning("User not found for in-memory removal", username=username)
        return False
