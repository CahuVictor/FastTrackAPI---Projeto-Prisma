# app/repositories/user.py
import abc

from app.schemas.user import UserInDB

class AbstractUserRepo(abc.ABC):
    @abc.abstractmethod
    def get_by_username(self, username: str) -> UserInDB | None:
        """."""
    
    @abc.abstractmethod
    def list_all(self) -> list[UserInDB]:
        """."""
    
    @abc.abstractmethod
    def add(self, user: UserInDB) -> UserInDB:
        """."""
    
    @abc.abstractmethod
    def delete_by_username(self, username: str) -> bool:
        """."""
