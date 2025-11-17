# app/infra/repositories/inmemory/local_repo_inmemory.py
from __future__ import annotations

from structlog import get_logger
from typing import Dict, List
from datetime import datetime

from app.models.local import Local
from app.models.venue_type import VenueType
from app.repositories.local_repo import LocalRepository

logger = get_logger().bind(module="local_repo_inmemory")


class LocalRepoInMemory(LocalRepository):
    """
    In-memory implementation of LocalRepository.

    This repository is meant for:
    - Unit tests.
    - Development environments without a real database.
    - Quick prototypes and experiments.

    It keeps behavior aligned with the SQLAlchemy version:
    - Auto-generates `id`.
    - Sets `created_at` when inserting.
    - Updates `updated_at` when modifying.
    - Stores Local entities in a simple in-memory dict.
    """

    def __init__(self) -> None:
        """
        Initializes an empty in-memory store and an ID counter.
        """
        self._storage: Dict[int, Local] = {}
        self._next_id: int = 1

        logger.debug("LocalRepoInMemory initialized")

    def _generate_id(self) -> int:
        """
        Generates a new incremental ID for in-memory locals.

        Returns:
            New integer ID.
        """
        new_id = self._next_id
        self._next_id += 1
        return new_id

    # ----------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------
    def add(self, local: Local) -> Local:
        """
        Adds a new Local to the in-memory store.

        If `local.id` is None, an incremental ID is assigned.
        `created_at` and `updated_at` are set to the current UTC time.

        Args:
            local: Domain Local entity to be stored.

        Returns:
            The same Local entity with `id`, `created_at` and `updated_at` populated.
        """
        if local.id is None:
            local.id = self._generate_id()

        now = datetime.utcnow()
        local.created_at = now
        local.updated_at = now

        self._storage[local.id] = local

        logger.info(
            "Local added in memory",
            local_id=local.id,
            location_name=local.location_name,
            capacity=local.capacity,
            is_accessible=local.is_accessible,
        )

        return local

    # ----------------------------------------------------------------------
    # READ
    # ----------------------------------------------------------------------
    def get(self, local_id: int) -> Local | None:
        """
        Retrieves a Local from the in-memory store by its ID.

        Args:
            local_id: Identifier of the Local to be retrieved.

        Returns:
            The Local if found, or None if it does not exist.
        """
        local = self._storage.get(local_id)

        if local:
            logger.info(
                "Local found in memory",
                local_id=local_id,
                location_name=local.location_name,
                capacity=local.capacity,
            )
        else:
            logger.info("Local not found in memory", local_id=local_id)

        return local

    # ----------------------------------------------------------------------
    # LIST
    # ----------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        location_name: str | None = None,
        capacity: int | None = None,
        venue_type: VenueType | None = None,
        is_accessible: bool | None = None,
        address: str | None = None,
        manually_edited: bool | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> List[Local]:
        """
        Returns a paginated slice of locals with optional filters.

        Locals are sorted by `location_name` in ascending order.

        Args:
            skip: Number of records to skip from the beginning.
            limit: Maximum number of records to return; if <= 0, no limit is applied.
            location_name: If provided, filters locals whose `location_name`
                contains this value (case-insensitive).
            capacity: If provided, filters locals whose `capacity` matches exactly.
            venue_type: If provided, filters locals by `venue_type` equality.
            is_accessible: If provided, filters by the accessibility flag.
            address: If provided, filters locals whose `address` contains this
                value (case-insensitive).
            manually_edited: If provided, filters by the `manually_edited` flag.
            created_at: If provided, keeps only locals with `created_at`
                greater than or equal to this value.
            updated_at: If provided, keeps only locals with `updated_at`
                greater than or equal to this value.

        Returns:
            A list of Local entities matching the filter and pagination.
        """
        locals_list = list(self._storage.values())

        if location_name is not None:
            needle = location_name.lower()
            locals_list = [
                l
                for l in locals_list
                if needle in l.location_name.lower()
            ]

        if capacity is not None:
            locals_list = [l for l in locals_list if l.capacity == capacity]

        if venue_type is not None:
            locals_list = [l for l in locals_list if l.venue_type == venue_type]

        if is_accessible is not None:
            locals_list = [l for l in locals_list if l.is_accessible == is_accessible]

        if address is not None:
            needle_addr = address.lower()
            locals_list = [
                l
                for l in locals_list
                if l.address is not None and needle_addr in l.address.lower()
            ]

        if manually_edited is not None:
            locals_list = [
                l for l in locals_list if l.manually_edited == manually_edited
            ]

        if created_at is not None:
            locals_list = [
                l
                for l in locals_list
                if l.created_at is not None and l.created_at >= created_at
            ]

        if updated_at is not None:
            locals_list = [
                l
                for l in locals_list
                if l.updated_at is not None and l.updated_at >= updated_at
            ]

        # Sort by name for deterministic behavior
        locals_list.sort(key=lambda l: l.location_name.lower())

        if skip:
            locals_list = locals_list[skip:]

        if limit > 0:
            locals_list = locals_list[:limit]

        logger.info(
            "Listing locals in memory",
            total=len(locals_list),
            skip=skip,
            limit=limit,
            location_name=location_name,
            capacity=capacity,
            venue_type=str(venue_type) if venue_type else None,
            is_accessible=is_accessible,
            manually_edited=manually_edited,
            created_at=created_at,
            updated_at=updated_at,
        )

        return locals_list

    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update(self, local: Local) -> Local:
        """
        Updates an existing Local in the in-memory store.

        `updated_at` is automatically refreshed to the current UTC time.

        Args:
            local: Local entity containing the new state. It must have a valid `id`.

        Returns:
            The updated Local entity.

        Raises:
            ValueError: If `local.id` is None.
            KeyError: If no record exists for the informed `id`.
        """
        if local.id is None:
            logger.error("Attempt to update in memory without id", local=local)
            raise ValueError("Cannot update Local without id")

        if local.id not in self._storage:
            logger.warning(
                "Local not found in memory for update",
                local_id=local.id,
            )
            raise KeyError("Local not found")

        local.updated_at = datetime.utcnow()
        self._storage[local.id] = local

        logger.info(
            "Local updated in memory",
            local_id=local.id,
            location_name=local.location_name,
            capacity=local.capacity,
            is_accessible=local.is_accessible,
        )

        return local

    # ----------------------------------------------------------------------
    # REPLACE ALL
    # ----------------------------------------------------------------------
    def replace_all(self, locals: List[Local]) -> List[Local]:
        """
        Replaces all Locals in the in-memory store with the given list.

        Behavior:
        - Clears the current storage.
        - Rebuilds it from the provided list.
        - Ensures the internal ID counter continues from the highest ID + 1.
        - If a Local has `id=None`, a new ID is generated.

        Args:
            locals: List of Local entities that will represent the new state.

        Returns:
            The list of persisted Local entities (with IDs ensured).
        """
        self._storage.clear()
        self._next_id = 1

        for local in locals:
            if local.id is None:
                local.id = self._generate_id()
            else:
                # garante que o contador ficará acima do maior ID informado
                if local.id >= self._next_id:
                    self._next_id = local.id + 1
            self._storage[local.id] = local

        logger.info(
            "All locals were replaced in memory",
            total=len(self._storage),
        )

        return list(self._storage.values())

    # ----------------------------------------------------------------------
    # REPLACE BY ID
    # ----------------------------------------------------------------------
    def replace_by_id(self, local_id: int, local: Local) -> Local:
        """
        Replaces a specific Local identified by its ID.

        Args:
            local_id: ID of the Local to be replaced.
            local: Local entity containing the new state.

        Returns:
            The Local entity after replacement.

        Raises:
            KeyError: If no record exists for the informed `local_id`.
        """
        if local_id not in self._storage:
            logger.warning(
                "Attempt to replace non-existing Local in memory",
                local_id=local_id,
            )
            raise KeyError("Local not found")

        local.id = local_id
        local.updated_at = datetime.utcnow()
        self._storage[local_id] = local

        logger.info(
            "Local replaced in memory",
            local_id=local_id,
            location_name=local.location_name,
            capacity=local.capacity,
        )

        return local

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def delete(self, local_id: int) -> bool:
        """
        Removes a Local from the in-memory store, if it exists.

        Args:
            local_id: Identifier of the Local to be removed.

        Returns:
            True if the Local was removed, False if it did not exist.
        """
        if local_id in self._storage:
            del self._storage[local_id]
            logger.info("Local removed from memory", local_id=local_id)
            return True

        logger.info(
            "Attempt to remove non-existing Local from memory",
            local_id=local_id,
        )
        return False
