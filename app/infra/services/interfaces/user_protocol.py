# app/repositories/user.py
from typing import Protocol
from app.schemas.user import UserInDB

class AbstractUserRepo(Protocol):
    def get_by_username(self, username: str) -> UserInDB | None: ...
