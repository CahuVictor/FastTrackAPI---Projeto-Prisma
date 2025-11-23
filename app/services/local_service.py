# app/services/local_service.py
from __future__ import annotations

from datetime import datetime
from typing import List
from structlog import get_logger
import httpx
import re
import unicodedata

from app.models.event_local_enums import VenueType
from app.models.local import Local
from app.models.local import LocalSource
from app.repositories.local_repo import LocalRepository
from app.schemas.local.local_create import LocalCreate
from app.schemas.local.local_update import LocalUpdate
from app.utils.text_normalization import normalize_text

class DuplicateLocalError(Exception):
    """Raised when attempting to create or update a Local that already exists
    with the same normalized (location_name, venue_type, address)."""
    pass

logger = get_logger().bind(module="local_service")


class LocalService:
    """
    Application service responsible for Local use cases.

    Responsibilities:
    - Mapping between schemas and the domain model (Local).
    - Enforcing business rules (manual override vs. external source).
    - Calling the repository (LocalRepository).
    """

    def __init__(self, repo: LocalRepository) -> None:
        """
        Args:
            repo: Concrete implementation of LocalRepository
                  (SQLAlchemy, InMemory, etc.).
        """
        self.repo = repo

    # ------------------------------------------------------------------ #
    # Basic CRUD (internal Local management / fallback for external API)
    # ------------------------------------------------------------------ #
    def list_locals(
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
        List locals with pagination and optional filters.

        This endpoint returns the locals that the system is effectively using,
        regardless of whether they were originally fetched from the internal
        LocalInfo API or manually created/edited as a fallback.

        Args:
            skip: How many records to skip (offset).
            limit: Maximum number of records to return.
            location_name: Partial or full name to filter by.
            capacity: Exact capacity filter.
            venue_type: Filter by venue type.
            is_accessible: Filter by accessibility flag.
            address: Partial address filter.
            manually_edited: Filter by manual override flag.
            created_at: Return only locals created on or after this timestamp.
            updated_at: Return only locals updated on or after this timestamp.

        Returns:
            A list of Local entities.
        """
        locals_ = self.repo.list(
            skip=skip,
            limit=limit,
            location_name=location_name,
            capacity=capacity,
            venue_type=venue_type,
            is_accessible=is_accessible,
            address=address,
            manually_edited=manually_edited,
            created_at=created_at,
            updated_at=updated_at,
        )
        logger.info(
            "Locals listed successfully",
            total=len(locals_),
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
        return locals_

    def list_all_locals(self) -> List[Local]:
        """
        List all locals without pagination.

        This method is mainly intended for internal use, such as
        background jobs or administrative tooling.
        """
        locals_ = self.repo.list(
            skip=0,
            limit=0,
            location_name=None,
            capacity=None,
            venue_type=None,
            is_accessible=None,
            address=None,
            manually_edited=None,
            created_at=None,
            updated_at=None,
        )
        logger.info("All locals listed", total=len(locals_))
        return locals_

    def get_local(self, local_id: int) -> Local | None:
        """
        Retrieve a local by ID.

        Args:
            local_id: Identifier of the local.

        Returns:
            Local if found, or None otherwise.
        """
        local = self.repo.get(local_id)
        if local:
            logger.info("Local retrieved", local_id=local_id, location_name=local.location_name)
        else:
            logger.info("Local not found in get_local", local_id=local_id)
        return local

    def create_local(self, payload: LocalCreate) -> Local:
        """
        Create a new Local from the input payload.

        Business rules:
        - It is not allowed to have two Locals with the same combination of
          (location_name, venue_type, address), when:
            * comparison is case-insensitive;
            * accents are ignored;
            * non-alphanumeric characters are ignored.
        - Every Local created here is considered a manual override.
        
        Any Local created through this service is considered a manual override
        unless a specific source is explicitly provided.
        """
        source = payload.source or LocalSource.MANUAL
        
        if self._is_duplicate_local(
            location_name=payload.location_name,
            venue_type=payload.venue_type,
            address=payload.address,
            exclude_id=None,
        ):
            logger.warning(
                "Attempt to create duplicate Local",
                location_name=payload.location_name,
                venue_type=str(payload.venue_type) if payload.venue_type else None,
                address=payload.address,
            )
            raise DuplicateLocalError(
                "A Local with the same name, venue type and address already exists"
            )

        local = Local(
            location_name=payload.location_name,
            capacity=payload.capacity,
            venue_type=payload.venue_type,
            is_accessible=payload.is_accessible,
            address=payload.address,
            manually_edited=True,
            external_id=payload.external_id,
            source=source,
            is_indoor=payload.is_indoor,
            has_cover=payload.has_cover,
            capacity_seated=payload.capacity_seated,
            capacity_standing=payload.capacity_standing,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone=payload.timezone,
        )
        created = self.repo.add(local)
        logger.info("Local created successfully", local_id=created.id, location_name=created.location_name, source=created.source,)
        return created

    def update_local(self, local_id: int, payload: LocalUpdate) -> Local:
        """
        Apply a partial update (patch) to an existing Local.

        Business rules:
        - If the Local does not exist, raises KeyError.
        - Any update performed here marks the Local as `manually_edited=True`.
        - The same uniqueness rule as in create_local is enforced:
          there cannot be another Local with the same normalized
          (location_name, venue_type, address).

        Raises:
            KeyError: If the Local is not found.
            DuplicateLocalError: If the update would violate the uniqueness rule.
        
        Any update performed through this service marks the Local as a
        manual override (unless explicitly configured otherwise).
        """
        local = self.repo.get(local_id)
        if not local:
            logger.warning("Attempt to update non-existing Local", local_id=local_id)
            raise KeyError("Local not found")

        if payload.location_name is not None:
            local.location_name = payload.location_name
        if payload.capacity is not None:
            local.capacity = payload.capacity
        if payload.venue_type is not None:
            local.venue_type = payload.venue_type
        if payload.is_accessible is not None:
            local.is_accessible = payload.is_accessible
        if payload.address is not None:
            local.address = payload.address
        
        if payload.external_id is not None:
            local.external_id = payload.external_id
        if payload.source is not None:
            local.source = payload.source
        if payload.is_indoor is not None:
            local.is_indoor = payload.is_indoor
        if payload.has_cover is not None:
            local.has_cover = payload.has_cover
        if payload.capacity_seated is not None:
            local.capacity_seated = payload.capacity_seated
        if payload.capacity_standing is not None:
            local.capacity_standing = payload.capacity_standing
        if payload.latitude is not None:
            local.latitude = payload.latitude
        if payload.longitude is not None:
            local.longitude = payload.longitude
        if payload.timezone is not None:
            local.timezone = payload.timezone
        
        if payload.manually_edited is not None:
            # The caller can force the flag, but we also ensure it becomes True
            local.manually_edited = payload.manually_edited

        # Always mark as manually edited after any update in our system
        local.manually_edited = True
        
        # Enforce uniqueness after applying changes
        if self._is_duplicate_local(
            location_name=local.location_name,
            venue_type=local.venue_type,
            address=local.address,
            exclude_id=local_id,
        ):
            logger.warning(
                "Attempt to update Local into a duplicate combination",
                local_id=local_id,
                location_name=local.location_name,
                venue_type=str(local.venue_type) if local.venue_type else None,
                address=local.address,
            )
            raise DuplicateLocalError(
                "Another Local with the same name, venue type and address already exists"
            )

        updated = self.repo.update(local)
        logger.info("Local updated successfully", local_id=updated.id, source=updated.source)
        return updated

    def delete_local(self, local_id: int) -> None:
        """
        Delete an existing Local.

        Raises:
            KeyError: If the Local is not found.
        """
        local = self.repo.get(local_id)
        if not local:
            logger.warning("Attempt to delete non-existing Local", local_id=local_id)
            raise KeyError("Local not found")

        self.repo.delete(local_id)
        logger.info("Local deleted successfully", local_id=local_id)
    
    def create_locals_batch(self, payloads: List[LocalCreate]) -> List[Local]:
        """
        Create multiple Locals in a single batch operation.

        Rules:
        - If the list is empty, returns an empty list (the controller may
          decide to treat this as 400).
        - The same uniqueness rule is enforced for each Local.
        - If a duplicate is found (either against existing database entries
          or against a Local already created in this batch), a
          DuplicateLocalError is raised and the batch is aborted.

        Returns:
            List of newly created Local entities.
        """
        created_locals: List[Local] = []

        for payload in payloads:
            # We rely on create_local, which already enforces uniqueness
            created = self.create_local(payload)
            created_locals.append(created)

        logger.info(
            "Locals created in batch",
            total=len(created_locals),
        )
        return created_locals

    # ------------------------------------------------------------------ #
    # External integration (placeholder)
    # ------------------------------------------------------------------ #
    async def get_info_by_coordinates(self, lat: float, lon: float) -> None:
        """
        Example of an integration with the internal LocalInfo API.

        This method is kept as a placeholder. Once the API contract is defined,
        you can:
        - Build the URL.
        - Perform the HTTP GET with httpx.
        - Map the response into a Local instance.
        - Optionally persist or update the Local in the repository,
          setting `manually_edited = False` for data coming from the
          internal system.
        """
        # base_url = get_service_url("local_info_url")
        # url = f"{base_url}/local_info?lat={lat}&lon={lon}"
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, timeout=10)
        #     response.raise_for_status()
        #     data = response.json()
        #
        # return Local(**data)
        return None
    
    # ------------------------------------------------------------------ #
    # External LocalInfo API integration (search)
    # ------------------------------------------------------------------ #
    async def search_locals_external(
        self,
        *,
        location_name: str | None = None,
        capacity_min: int | None = None,
        capacity_max: int | None = None,
        venue_types: list[VenueType] | None = None,
        is_accessible: bool | None = None,
        address: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Local]:
        """
        Search venues in the internal LocalInfo API.

        This does NOT necessarily persist the results in our database.
        It returns domain Local objects so that the caller can decide whether
        to:
        - just show a preview to the user; or
        - import one or more venues into our own Local repository.

        Args:
            location_name: Name or partial name to search for (fuzzy match).
            capacity_min: Minimum capacity (inclusive).
            capacity_max: Maximum capacity (inclusive).
            venue_types: List of allowed venue types.
            is_accessible: Filter by accessibility flag.
            address: Address or partial address for fuzzy search.
            skip: Pagination offset.
            limit: Pagination limit.

        Returns:
            A list of Local domain entities built from the external payload.
        """
        payload = self._build_external_search_payload(
            location_name=location_name,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            venue_types=venue_types,
            is_accessible=is_accessible,
            address=address,
            skip=skip,
            limit=limit,
        )

        logger.info("Calling external Local API", payload=payload)

        # TODO: Replace with the real base URL and endpoint path.
        base_url = "https://local.internal/api"
        search_url = f"{base_url}/venues/search"
        
        # For now, this integration is intentionally not implemented.
        # The controller is responsible for catching this error and
        # translating it into a 501 HTTP response.
        raise NotImplementedError("External LocalInfo API integration not implemented yet")

        # Placeholder HTTP call – adjust according to the real contract
        # async with httpx.AsyncClient() as client:
            # NOTE: choose GET with params or POST with JSON depending on the API
            # response = await client.get(search_url, params=payload, timeout=10)
            # or:
            # response = await client.post(search_url, json=payload, timeout=10)
            #
            # For now we keep it as NotImplemented so tests fail loudly
            # raise NotImplementedError("External LocalInfo API integration not implemented yet")

            # response.raise_for_status()
            # data = response.json()

        # Assuming `data` is a list of dicts representing venues:
        # results: list[Local] = [
        #     self._map_external_local_to_domain(raw)
        #     for raw in data
        # ]
        #
        # return results

    def _build_external_search_payload(
        self,
        *,
        location_name: str | None,
        capacity_min: int | None,
        capacity_max: int | None,
        venue_types: list[VenueType] | None,
        is_accessible: bool | None,
        address: str | None,
        skip: int,
        limit: int,
    ) -> dict:
        """
        Build the payload (or query parameters) for the external LocalInfo API.

        This function defines how we send filters to the external service,
        independent of how we persist our own Local entities.
        """
        payload: dict[str, Any] = {
            "skip": skip,
            "limit": limit,
        }

        if location_name is not None:
            payload["location_name"] = location_name

        if capacity_min is not None:
            payload["capacity_min"] = capacity_min

        if capacity_max is not None:
            payload["capacity_max"] = capacity_max

        if venue_types:
            # Usually we send enum values as strings to external APIs.
            payload["venue_types"] = [vt.value for vt in venue_types]

        if is_accessible is not None:
            payload["is_accessible"] = is_accessible

        if address is not None:
            payload["address"] = address

        return payload

    def _map_external_local_to_domain(self, raw: dict) -> Local:
        """
        Map a single record from the external LocalInfo API into
        our Local domain model.

        The exact keys in `raw` depend on the external API contract.

        Here we define how WE want to interpret that payload.
        """
        # Example mapping – adjust when you know the real contract:
        return Local(
            id=None,  # external system should not define our internal id
            location_name=raw.get("name") or raw.get("location_name", "Unknown"),
            capacity=int(raw.get("capacity", 0)),
            venue_type=self._map_external_venue_type(raw.get("venue_type")),
            is_accessible=bool(raw.get("is_accessible", False)),
            address=raw.get("address"),
            manually_edited=False,  # coming from external system
            created_at=None,
            updated_at=None,
        )

    def _map_external_venue_type(self, raw_venue_type: str | None) -> VenueType | None:
        """
        Convert the external venue_type representation into our VenueType enum.

        If the value is unknown or None, returns None.
        """
        if raw_venue_type is None:
            return None

        try:
            # If external values match our enum names or values directly:
            return VenueType(raw_venue_type)
        except ValueError:
            logger.warning(
                "Unknown external venue_type received",
                external_value=raw_venue_type,
            )
            return None
    
    # ------------------------------------------------------------------ #
    # Uniqueness rule helpers
    # ------------------------------------------------------------------ #
    def _is_duplicate_local(
        self,
        *,
        location_name: str,
        venue_type: VenueType | None,
        address: str | None,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Checks whether there is already a Local with the same
        (location_name, venue_type, address) combination.

        Comparison is:
        - case-insensitive,
        - accent-insensitive,
        - ignores non-alphanumeric characters in text fields.

        Args:
            location_name: Candidate location name.
            venue_type: Candidate venue type.
            address: Candidate address.
            exclude_id: If informed, ignores this Local ID in the comparison
                        (used when updating an existing Local).

        Returns:
            True if another Local with the same normalized triple exists,
            False otherwise.
        """
        norm_name = normalize_text(location_name)
        norm_addr = normalize_text(address)

        for existing in self.list_all_locals():
            if exclude_id is not None and existing.id == exclude_id:
                continue

            if normalize_text(existing.location_name) != norm_name:
                continue

            if existing.venue_type != venue_type:
                continue

            if normalize_text(existing.address) != norm_addr:
                continue

            return True

        return False
    
    async def sync_local_from_external(self, local_id: int) -> Local:
        """
        Synchronize a single Local with the external LocalInfo API.

        Flow (to be implemented when the API contract is known):
        - Load the Local by ID.
        - If it has no `external_id`, decide whether to:
            - error (404 / bad request), or
            - infer an external identifier based on internal data.
        - Call the external LocalInfo API.
        - Map the response payload to the Local domain model.
        - Apply update rules:
            - If local.source == MANUAL or local.manually_edited == True,
              only update "safe" fields (e.g. latitude/longitude).
            - Otherwise, allow a broader overwrite.
        - Persist and return the updated Local.
        """
        local = self.repo.get(local_id)
        if not local:
            logger.warning("Attempt to sync non-existing Local", local_id=local_id)
            raise KeyError("Local not found")

        # Placeholder for now
        logger.info(
            "sync_local_from_external called but not implemented",
            local_id=local_id,
            external_id=local.external_id,
        )
        raise NotImplementedError("External LocalInfo API sync not implemented yet")

    async def import_locals_from_external(
        self,
        *,
        location_name: str | None = None,
        capacity_min: int | None = None,
        capacity_max: int | None = None,
        venue_types: list[VenueType] | None = None,
        is_accessible: bool | None = None,
        address: str | None = None,
        limit: int = 50,
    ) -> list[Local]:
        """
        Import Locals from the external LocalInfo API into the internal repository.

        Flow (to be implemented):
        - Build a payload with the given filters.
        - Call the external LocalInfo API.
        - For each result, map it to a Local entity.
        - Decide whether to:
            - create new Local (source=INTERNAL_SYNC),
            - update existing ones based on external_id,
            - or skip duplicates.
        - Return the list of persisted Local entities.
        """
        logger.info(
            "import_locals_from_external called but not implemented",
            location_name=location_name,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            venue_types=[str(v) for v in venue_types] if venue_types else None,
            is_accessible=is_accessible,
            address=address,
            limit=limit,
        )
        raise NotImplementedError("External LocalInfo bulk import not implemented yet")
    
    def _build_conflict_key(self, local: Local) -> str:
        """
        Build a normalized key used to detect possible duplicate Locals.

        The key combines normalized location_name, address and venue_type.
        """
        name_norm = normalize_text(local.location_name or "")
        addr_norm = normalize_text(local.address or "")
        venue_norm = (
            normalize_text(local.venue_type.value) if local.venue_type is not None else ""
        )
        return "|".join([name_norm, addr_norm, venue_norm])

    def find_conflicting_locals(self) -> list[list[Local]]:
        """
        Find groups of Locals that are likely duplicates of each other.

        Two Locals are considered in conflict if they share the same
        normalized (location_name, address, venue_type) key.
        """
        all_locals = self.list_all_locals()
        buckets: Dict[str, List[Local]] = defaultdict(list)

        for local in all_locals:
            key = self._build_conflict_key(local)
            buckets[key].append(local)

        conflict_groups = [group for group in buckets.values() if len(group) > 1]

        logger.info(
            "Conflicting locals computed",
            total_groups=len(conflict_groups),
            total_locals=sum(len(g) for g in conflict_groups),
        )
        return conflict_groups

    def merge_locals(self, target_id: int, source_ids: list[int]) -> Local:
        """
        Merge multiple Local records into a single target Local.

        Current behavior:
        - Ensures all source Locals exist.
        - Does NOT update events or other references yet (TODO).
        - Deletes source Locals from the repository.
        - Returns the target Local.

        Args:
            target_id: The Local that will remain after the merge.
            source_ids: List of Local IDs to be merged into the target.
                        The target_id must not appear in this list.

        Raises:
            KeyError: If the target or any source Local does not exist.
            ValueError: If target_id is included in source_ids.
        """
        if target_id in source_ids:
            raise ValueError("target_id must not be included in source_ids")

        target = self.repo.get(target_id)
        if not target:
            logger.warning("Target Local for merge not found", target_id=target_id)
            raise KeyError("Target Local not found")

        # validate existence of sources
        sources: list[Local] = []
        for sid in source_ids:
            local = self.repo.get(sid)
            if not local:
                logger.warning("Source Local for merge not found", local_id=sid)
                raise KeyError(f"Source Local not found: {sid}")
            sources.append(local)

        # TODO: in the future, update events referencing source_ids to target_id

        # remove sources
        for src in sources:
            self.repo.delete(src.id)  # type: ignore[arg-type]

        logger.info(
            "Locals merged",
            target_id=target_id,
            source_ids=source_ids,
        )
        return target