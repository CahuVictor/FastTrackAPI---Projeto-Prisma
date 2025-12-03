# app/infra/repositories/inmemory/local_repo_inmemory.py
from __future__ import annotations

from structlog import get_logger
from typing import Dict, List
from datetime import datetime

from app.models.local import Local
from app.models.local_filters import LocalFilterCriteria
from app.models.enums import VenueType
from app.repositories.local_repo import LocalRepository

logger = get_logger().bind(module="local_repo_inmemory")

def _apply_filter_and_sort(
    locals_list: list[Local],
    filter: LocalFilterCriteria,
) -> list[Local]:
    """
    Apply the in-memory filtering and sorting logic over a list of Locals.

    This helper keeps the `list` method smaller and centralizes all
    filter conditions in one place. It also documents the fact that,
    in this in-memory implementation, all data is loaded into memory
    before applying filters — which is different from a future SQL
    implementation, where filters should be translated to WHERE clauses.
    """
    # Filtros básicos de string / igualdade
    if filter.name is not None:
        needle = filter.name.lower()
        locals_list = [l for l in locals_list if needle in l.name.lower()]

    if filter.capacity is not None:
        locals_list = [l for l in locals_list if l.capacity == filter.capacity]

    if filter.is_accessible is not None:
        locals_list = [l for l in locals_list if l.is_accessible == filter.is_accessible]

    if filter.parking_available is not None:
        locals_list = [l for l in locals_list if l.parking_available == filter.parking_available]

    if filter.latitude is not None:
        locals_list = [l for l in locals_list if l.latitude == filter.latitude]

    if filter.longitude is not None:
        locals_list = [l for l in locals_list if l.longitude == filter.longitude]

    if filter.external_id is not None:
        locals_list = [l for l in locals_list if l.external_id == filter.external_id]

    if filter.source is not None:
        locals_list = [l for l in locals_list if l.source == filter.source]

    if filter.is_indoor is not None:
        locals_list = [l for l in locals_list if l.is_indoor == filter.is_indoor]

    if filter.has_cover is not None:
        locals_list = [l for l in locals_list if l.has_cover == filter.has_cover]

    if filter.capacity_seated is not None:
        locals_list = [l for l in locals_list if l.capacity_seated == filter.capacity_seated]

    if filter.capacity_standing is not None:
        locals_list = [l for l in locals_list if l.capacity_standing == filter.capacity_standing]

    if filter.venue_type is not None:
        locals_list = [l for l in locals_list if l.venue_type == filter.venue_type]

    if filter.manually_edited is not None:
        locals_list = [l for l in locals_list if l.manually_edited == filter.manually_edited]

    if filter.created_at is not None:
        locals_list = [
            l
            for l in locals_list
            if l.created_at is not None and l.created_at >= filter.created_at
        ]

    if filter.updated_at is not None:
        locals_list = [
            l
            for l in locals_list
            if l.updated_at is not None and l.updated_at >= filter.updated_at
        ]

    # Ordenação determinística
    locals_list.sort(key=lambda l: l.name.lower())

    # Paginação
    if filter.skip:
        locals_list = locals_list[filter.skip:]

    if filter.limit and filter.limit > 0:
        locals_list = locals_list[:filter.limit]

    return locals_list

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
            name=local.name,
            capacity=local.capacity,
            is_accessible=local.is_accessible,
            venue_type=str(local.venue_type) if local.venue_type else None,
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
                local_id=local.id,
                name=local.name,
                capacity=local.capacity,
                is_accessible=local.is_accessible,
                venue_type=str(local.venue_type) if local.venue_type else None,
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
        filter: LocalFilterCriteria | None = None,
    ) -> list[Local]:
        """
        Returns a paginated slice of locals with optional filters.

        In this in-memory implementation, all entities are loaded from the
        internal storage (a dict) and filters are applied in Python. In a
        future SQL-backed repository, this method should instead translate
        LocalFilterCriteria into SQL WHERE clauses so the database can apply
        indexes and optimizations.

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
        # `self._storage` is an in-memory dict[int, Local]. We take only its
        # values here, because we don't care about the keys for listing.
        # NOTE:
        # In this in-memory implementation we load all Locals from `_storage`
        # and apply filters in Python. In a future SQL-based repository, this
        # method should translate `LocalFilterCriteria` into SQL WHERE clauses
        # so that the database can apply indexes and optimizations.
        locals_list = list(self._storage.values())
        
        if filter is not None:
            locals_list = _apply_filter_and_sort(locals_list, filter)

        logger.info(
            "Listing locals in memory",
            total=len(locals_list),
            filter=filter,
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
            name=local.name,
            capacity=local.capacity,
            is_accessible=local.is_accessible,
            venue_type=str(local.venue_type) if local.venue_type else None,
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
            local_id=local.id,
            name=local.name,
            capacity=local.capacity,
            is_accessible=local.is_accessible,
            venue_type=str(local.venue_type) if local.venue_type else None,
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
