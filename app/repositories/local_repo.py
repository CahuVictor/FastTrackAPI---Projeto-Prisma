# app/repositories/local_repo.py
from __future__ import annotations

import abc
from datetime import datetime
from typing import List

from app.models.local import Local
from app.models.local_filters import LocalFilterCriteria
from app.models.event_local_enums import VenueType


class LocalRepository(abc.ABC):
    @abc.abstractmethod
    def list(
        self,
        *,
        filter: LocalFilterCriteria | None,
    ) -> list[Local]:
        """
        List locals with pagination and optional filters.
        """
	
    @abc.abstractmethod
    def get(self, local_id: int) -> Local | None:
        """
        Retrieve a single Local by ID.
        """
	
    @abc.abstractmethod
    def add(self, local: Local) -> Local:
        """
        Persist a new Local entity.
        """
	
    @abc.abstractmethod
    def replace_all(self, locals: list[Local]) -> list[Local]:
        """
        Replace all Local entries with the given list.
        """
	
    @abc.abstractmethod
    def replace_by_id(self, local_id: int, local: Local) -> Local:
        """
        Replace a specific Local by ID.
        """
    
    # @abc.abstractmethod
    # def delete(self) -> None:
    #     """."""
    
    @abc.abstractmethod
    def delete(self, local_id: int) -> bool:
        """
        Delete a Local by ID. Returns True if an entity was deleted.
        """
	
    @abc.abstractmethod
    def update(self, local: Local) -> Local:
        """
        Update an existing Local entity.
        """

