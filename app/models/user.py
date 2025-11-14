# app/models/user.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass(slots=True, kw_only=True)
class User:
    id: int | None = None
    username: str
    full_name: str | None = None
    hashed_password: str
    roles: List[str]

    @classmethod
    def from_roles_str(
        cls,
        *,
        id: int | None,
        username: str,
        full_name: str | None,
        hashed_password: str,
        roles_str: str,
    ) -> "User":
        roles = [r.strip() for r in roles_str.split(",") if r.strip()]
        return cls(
            id=id,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            roles=roles,
        )

    def roles_as_str(self) -> str:
        return ",".join(self.roles)

    def has_role(self, role: str) -> bool:
        return role in self.roles
