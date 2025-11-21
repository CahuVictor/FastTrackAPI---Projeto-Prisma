# app/models/user.py
"""
Domain model for `User`.

This dataclass represents the *core* user entity used by the domain layer.
It is intentionally decoupled from:
- database details (SQLAlchemy models);
- HTTP/Pydantic schemas.

The idea is that repositories and services can use this type as the
canonical representation of a user inside the application core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class User:
    """
    Domain entity representing a system user.

    Attributes:
        id: Internal database identifier (optional).
        username: Unique username used for login/identification.
        full_name: Optional full name for display.
        hashed_password: Password already hashed using the chosen algorithm.
        roles: List of roles associated with this user (e.g., ["admin", "editor"]).
        created_at: Timestamp of creation (if tracked by persistence).
        updated_at: Timestamp of last update (if tracked by persistence).
    """

    id: int | None = None
    username: str
    full_name: str | None = None
    hashed_password: str
    roles: List[str]
    
    # Audit fields
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_roles_str(
        cls,
        *,
        id: int | None,
        username: str,
        full_name: str | None,
        hashed_password: str,
        roles_str: list[str],
        
        # Audit fields
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "User":
        """
        Factory method to build a User from a comma-separated roles string.

        Args:
            roles_str: String in the format "admin,editor,viewer".

        Returns:
            User domain object.
        """
        roles = [r.strip() for r in roles_str.split(",") if r.strip()]
        return cls(
            id=id,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            roles=roles,
            created_at=created_at,
            updated_at=updated_at,
        )

    def roles_as_str(self) -> str:
        """
        Return roles as a single comma-separated string.

        Useful when persisting the entity back to a database column.
        """
        return ",".join(self.roles)

    def has_role(self, role: str) -> bool:
        """
        Check if the user has a specific role.

        Args:
            role: Role name to check, e.g. "admin".

        Returns:
            True if the role is present, False otherwise.
        """
        return role in self.roles