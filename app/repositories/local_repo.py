# app/repositories/local.py
from __future__ import annotations

import abc

from app.models.local import Local

class LocalRepository(abc.ABC):    
    @abc.abstractmethod
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
        # **filters
    ) -> list[Local]:
        """."""
    
    @abc.abstractmethod
    def get(self, local_id: int) -> Local | None:
        """."""
    
    @abc.abstractmethod
    def add(self, local: Local) -> Local:
        """."""
    
    @abc.abstractmethod
    def replace_all(self, locals: list[Local]) -> list[Local]:
        """."""
    
    @abc.abstractmethod
    def replace_by_id(self, local_id: int, local: Local) -> Local:
        """."""
    
    @abc.abstractmethod
    def delete(self) -> None:
        """."""
    
    @abc.abstractmethod
    def delete(self, local_id: int) -> bool:
        """."""
    
    @abc.abstractmethod
    # def update(self, local_id: int, data: dict) -> local:
    def update(self, local: Local) -> Local:
        """."""
    
