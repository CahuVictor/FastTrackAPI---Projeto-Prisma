# app/services/local_service.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Set
from structlog import get_logger
import inspect

from app.models.local import Local
from app.models.local_filters import LocalFilterCriteria
from app.models.local_external_query import ExternalLocalQueryCriteria
from app.models.enums import VenueType, LocalSource
from app.repositories.local_repo import LocalRepository
from app.schemas.local.local_create import LocalCreate
from app.schemas.local.local_update import LocalUpdate
from app.utils.text_normalization import normalize_text
from app.services.errors import DuplicateLocalError

logger = get_logger().bind(module="local_service")


class LocalService:
    """
    Application service responsible for Local use cases.

    Responsibilities:
    - Mapping between schemas and the domain model (Local).
    - Enforcing business rules (manual override vs. external source).
    - Calling the repository (LocalRepository).
    """
    
    
    # ------------------------------------------------------------------ #
    # Internal helpers for field mapping and diagnostics
    # ------------------------------------------------------------------ #
    @staticmethod
    def _get_model_field_names(model_or_instance: Any) -> Set[str]:
        """
        Best-effort helper to retrieve field names from Pydantic v1/v2 models
        or plain dataclasses/objects.

        Returns:
            A set of field names for the given model/instance.
        """
        # Pydantic v2
        fields = getattr(model_or_instance, "model_fields", None)
        if isinstance(fields, dict):
            return set(fields.keys())

        # Pydantic v1
        fields = getattr(model_or_instance, "__fields__", None)
        if isinstance(fields, dict):
            return set(fields.keys())

        # Fallback: use __dict__ keys if it's an instance
        if hasattr(model_or_instance, "__dict__"):
            return set(model_or_instance.__dict__.keys())

        return set()

    def _log_unused_fields(
        self,
        context: str,
        source_name: str,
        used_fields: Set[str],
        model_or_instance: Any,
        ignore_fields: Set[str] | None = None,
    ) -> None:
        """
        Logs a warning if there are fields defined in the model that are not
        used by the mapping logic.

        Args:
            context: Logical context, e.g. "create_local" or "update_local".
            source_name: Name of the model, e.g. "LocalCreate" or "Local".
            used_fields: Set of field names that are actively mapped/used.
            model_or_instance: Pydantic model class/instance or dataclass.
            ignore_fields: Fields that are expected to be ignored (e.g. id).
        """
        all_fields = self._get_model_field_names(model_or_instance)
        ignored = ignore_fields or set()
        unused = all_fields - used_fields - ignored

        if unused:
            logger.warning(
                "Unused fields detected in mapping",
                context=context,
                model=source_name,
                unused_fields=sorted(unused),
            )

    def _build_local_from_create(self, payload: LocalCreate) -> Local:
        """
        Build a Local domain entity from a LocalCreate payload.

        This helper also:
        - Validates that all mapped fields exist in both LocalCreate and Local.
        - Raises ValueError if the mapping references a non-existing field.
        - Logs warnings for fields present in LocalCreate or Local that are
          not used by the mapping (to simplify future refactors/debugging).

        Returns:
            A Local domain entity (not yet persisted).
        """
        # Default source rule
        source = payload.source or LocalSource.MANUAL

        # # Explicit mapping between LocalCreate fields and Local fields
        # field_map: Dict[str, str] = {
        #     "location_name": "location_name",   # or "name" if o modelo estiver assim
        #     "capacity": "capacity",
        #     "venue_type": "venue_type",
        #     "is_accessible": "is_accessible",
        #     "address": "address",               # se Local ainda tiver "address"
        #     "external_id": "external_id",
        #     "is_indoor": "is_indoor",
        #     "has_cover": "has_cover",
        #     "capacity_seated": "capacity_seated",
        #     "capacity_standing": "capacity_standing",
        #     "latitude": "latitude",
        #     "longitude": "longitude",
        #     "timezone": "timezone",
        #     # source será calculado, mas também existe em Local/LocalCreate
        #     "source": "source",
        # }

        # # --- Validation of mapping against models -----------------------
        # payload_fields = self._get_model_field_names(LocalCreate)
        # local_fields = self._get_model_field_names(Local)

        # # All mapped source fields must exist in LocalCreate
        # for src in field_map.keys():
        #     if src not in payload_fields:
        #         raise ValueError(
        #             f"Mapping references field '{src}' which does not exist in LocalCreate"
        #         )

        # # All mapped target fields must exist in Local
        # for dst in field_map.values():
        #     if dst not in local_fields:
        #         raise ValueError(
        #             f"Mapping references field '{dst}' which does not exist in Local"
        #         )

        # used_payload_fields = set(field_map.keys())
        # used_local_fields = set(field_map.values())

        # # Fields we explicitly expect to be managed elsewhere in Local
        # ignore_local_fields: Set[str] = {
        #     "id",
        #     "created_at",
        #     "updated_at",
        #     "manually_edited",
        #     "parking_available",
        #     "images",
        #     "contact_phone",
        # }

        # # Log unused fields from LocalCreate and Local
        # self._log_unused_fields(
        #     context="create_local",
        #     source_name="LocalCreate",
        #     used_fields=used_payload_fields,
        #     model_or_instance=LocalCreate,
        # )
        # self._log_unused_fields(
        #     context="create_local",
        #     source_name="Local",
        #     used_fields=used_local_fields,
        #     model_or_instance=Local,
        #     ignore_fields=ignore_local_fields,
        # )

        # # --- Build the kwargs for Local ---------------------------------
        # local_kwargs: Dict[str, Any] = {}

        # for src, dst in field_map.items():
        #     value = getattr(payload, src)
        #     # Special handling for source: override with default if None
        #     if src == "source":
        #         value = source
        #     local_kwargs[dst] = value

        # # Extra defaults that are domain-specific
        # local_kwargs.setdefault("parking_available", False)
        # local_kwargs.setdefault("contact_phone", None)
        # local_kwargs.setdefault("images", [])
        # # Regra de negócio: criado manualmente → manual override
        # local_kwargs.setdefault(
        #     "manually_edited",
        #     source == LocalSource.MANUAL,
        # )

        # return Local(**local_kwargs)
        return Local(
            name=payload.name,
            capacity=payload.capacity,
            is_accessible=payload.is_accessible,
            parking_available=payload.parking_available,
            
            # Address Block
            address_street=payload.address_street,
            address_city=payload.address_city,
            address_state=payload.address_state,
            # 
            # # geo & timezone
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone=payload.timezone,
            # integration and origin metadata
            external_id=payload.external_id,
            source=source,
            
            # physical characteristics
            is_indoor=payload.is_indoor,
            has_cover=payload.has_cover,
            capacity_seated=payload.capacity_seated,
            capacity_standing=payload.capacity_standing,
            
            contact_phone=payload.contact_phone,
            images=payload.images,
            
            venue_type=payload.venue_type,
        )

    def _apply_update_from_payload(self, local: Local, payload: LocalUpdate) -> None:
        """
        Apply patch semantics from LocalUpdate to an existing Local entity.

        Fields with value None in payload are ignored.
        This helper also logs unused fields to help keep mapping and model aligned.
        """
        field_map: Dict[str, str] = {
            "location_name": "location_name",
            "capacity": "capacity",
            "venue_type": "venue_type",
            "is_accessible": "is_accessible",
            "address": "address",
            "external_id": "external_id",
            "source": "source",
            "is_indoor": "is_indoor",
            "has_cover": "has_cover",
            "capacity_seated": "capacity_seated",
            "capacity_standing": "capacity_standing",
            "latitude": "latitude",
            "longitude": "longitude",
            "timezone": "timezone",
            "manually_edited": "manually_edited",
        }

        payload_fields = self._get_model_field_names(LocalUpdate)
        local_fields = self._get_model_field_names(Local)

        # Validate mapping references
        for src in field_map.keys():
            if src not in payload_fields:
                raise ValueError(
                    f"Update mapping references field '{src}' "
                    f"which does not exist in LocalUpdate"
                )
        for dst in field_map.values():
            if dst not in local_fields:
                raise ValueError(
                    f"Update mapping references field '{dst}' "
                    f"which does not exist in Local"
                )

        used_payload_fields = set(field_map.keys())
        used_local_fields = set(field_map.values())

        ignore_local_fields: Set[str] = {
            "id",
            "created_at",
            "updated_at",
            "parking_available",
            "images",
            "contact_phone",
        }

        self._log_unused_fields(
            context="update_local",
            source_name="LocalUpdate",
            used_fields=used_payload_fields,
            model_or_instance=LocalUpdate,
        )
        self._log_unused_fields(
            context="update_local",
            source_name="Local",
            used_fields=used_local_fields,
            model_or_instance=Local,
            ignore_fields=ignore_local_fields,
        )

        # Apply only non-None values
        for src, dst in field_map.items():
            value = getattr(payload, src)
            if value is not None:
                setattr(local, dst, value)

        # Regra específica para manually_edited:
        # - Se o payload trouxer um valor explícito, respeitamos.
        # - Caso contrário, qualquer update feito pelo sistema marca como True.
        if payload.manually_edited is None:
            local.manually_edited = True

    def _from_filters_to_dict(self, filters: LocalFilterCriteria):
        # Dict com apenas campos preenchidos (None removido)
        raw_filters = filters.model_dump(exclude_none=True)

        # Descobre quais parâmetros o repositório realmente aceita
        repo_sig = inspect.signature(self.repo.list)
        allowed_keys = set(repo_sig.parameters.keys())

        repo_kwargs = {k: v for k, v in raw_filters.items() if k in allowed_keys}
        ignored_for_repo = set(raw_filters.keys()) - allowed_keys
        if ignored_for_repo:
            logger.warning(
                "Some LocalFilterCriteria fields are not supported by repository; ignoring",
                ignored_fields=sorted(ignored_for_repo),
            )
        
        return repo_kwargs

    # ------------------------------------------------------------------ #
    # Basic CRUD
    # ------------------------------------------------------------------ #
    
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
    def list_locals(self, filters: LocalFilterCriteria) -> list[Local]:
        """
        List locals with pagination and optional filters.

        This endpoint returns the locals that the system is effectively using,
        regardless of whether they were originally fetched from the internal
        LocalInfo API or manually created/edited as a fallback.
        
        This method returns the locals that the system is effectively using,
        regardless of whether they were originally fetched from the internal
        LocalInfo API or manually created/edited as a fallback.

        Unknown filters passed via **extra_filters are ignored, but a warning
        is logged so that callers and maintainers can align the contract.

        Args:
            filters: Strongly-typed filter DTO coming from the controller.

        Returns:
            A list of Local entities.
        """
        locals_ = self.repo.list(filters)
        
        logger.info(
            "Locals listed successfully",
            total=len(locals_),
            filters=filters,
        )
        return locals_

    def list_all_locals(self) -> List[Local]:
        """
        List all locals without pagination.

        This method is mainly intended for internal use, such as
        background jobs or administrative tooling.
        """    
        locals_ = self.repo.list()
        
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
            logger.info("Local retrieved", local_id=local_id, location_name=local.name)
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
        # Enforce uniqueness _before_ creating the entity
        if self._is_duplicate_local(
            name=payload.name,
            venue_type=payload.venue_type,
            address=None, # payload.address, # TODO
            exclude_id=None,
        ):
            logger.warning(
                "Attempt to create duplicate Local",
                name=payload.name,
                venue_type=str(payload.venue_type) if payload.venue_type else None,
                city=payload.address_city,
                state=payload.address_state,
                # TODO LATITUDE LONGITUDE?
            )
            raise DuplicateLocalError(
                "A Local with the same name, venue type and address already exists"
            )

        # Build the domain entity from the payload
        local = self._build_local_from_create(payload)
        
        created = self.repo.add(local)
        logger.info(
            "Local created successfully",
            local_id=created.id,
            location_name=created.name,
            source=created.source,
            created_at=created.created_at,
        )
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

        # Apply patch semantics from payload to entity
        self._apply_update_from_payload(local, payload)
        
        # Enforce uniqueness after applying changes
        if self._is_duplicate_local(
            name=local.name,
            venue_type=local.venue_type,
            address=None, # TODO
            exclude_id=None, # TODO
        ):
            logger.warning(
                "Attempt to update Local into a duplicate combination",
                local_id=local.id,
                name=local.name,
                capacity=local.capacity,
                is_accessible=local.is_accessible,
                venue_type=str(local.venue_type) if local.venue_type else None,
                
                
            )
            raise DuplicateLocalError(
                "Another Local with the same name, venue type and address already exists"
            )

        updated = self.repo.update(local)
        logger.info(
            "Local updated successfully",
            local_id=updated.id,
            source=updated.source
        )
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
        criteria: ExternalLocalQueryCriteria,
    ) -> list[Local]:
        """
        Search venues in the internal LocalInfo API.

        This does NOT necessarily persist the results in our database.
        It returns domain Local objects so that the caller can decide whether
        to:
        - just show a preview to the user; or
        - import one or more venues into our own Local repository.
        
        This method is responsible for:
        - Translating `ExternalLocalQueryCriteria` into the HTTP payload required
          by the external API.
        - Calling the external API client/integration.
        - Mapping the external payload into domain `Local` instances
          (without necessarily persisting them in the local repository).

        Args:
            criteria: 

        Returns:
            A list of Local domain entities built from the external payload.
        
        Raises:
            NotImplementedError: While the integration is not yet implemented.
        """
        payload = self._build_external_search_payload(criteria)

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
        criteria: ExternalLocalQueryCriteria,
    ) -> dict:
        """
        Build the payload (or query parameters) for the external LocalInfo API.

        This function defines how we send filters to the external service,
        independent of how we persist our own Local entities.
        """
        payload: dict[str, Any] = {
            "skip": criteria.skip,
            "limit": criteria.limit,
        }

        if criteria.name is not None:
            payload["location_name"] = criteria.name

        if criteria.capacity_min is not None:
            payload["capacity_min"] = criteria.capacity_min

        if criteria.capacity_max is not None:
            payload["capacity_max"] = criteria.capacity_max
            
        if criteria.is_accessible is not None:
            payload["is_accessible"] = criteria.is_accessible
        
        if criteria.is_accessible is not None:
            payload["is_accessible"] = criteria.is_accessible
        
        
        if criteria.latitude is not None:
            payload["is_accessible"] = criteria.latitude
        
        if criteria.longitude is not None:
            payload["is_accessible"] = criteria.longitude
        
        
        # external_id, 
        
        
        # Physical / capacity details
        if criteria.is_indoor is not None:
            payload["is_indoor"] = criteria.is_indoor
        
        if criteria.has_cover is not None:
            payload["has_cover"] = criteria.has_cover
        
        if criteria.capacity_seated is not None:
            payload["is_accessible"] = criteria.capacity_seated
        
        if criteria.capacity_standing is not None:
            payload["is_accessible"] = criteria.capacity_standing
        
        
        if criteria.venue_types:
            # Usually we send enum values as strings to external APIs.
            payload["venue_types"] = [vt.value for vt in criteria.venue_types]

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
    def _is_duplicate_local( # TODO atualizar para usar name, venue_type, latitude, longitude. Latitude e Longitude deve ser usado valores próximos calcular a distancia por exemplo
        self,
        *,
        name: str,
        venue_type: VenueType | None,
        address: str | None,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Checks whether there is already a Local with the same
        (name, venue_type, address) combination.

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
        norm_name = normalize_text(name)
        norm_addr = normalize_text(address)

        for existing in self.list_all_locals():
            if exclude_id is not None and existing.id == exclude_id:
                continue

            if normalize_text(existing.name) != norm_name:
                continue

            if existing.venue_type != venue_type:
                continue

            # if normalize_text(existing.address) != norm_addr: # TODO
            #     continue

            return True

        return False
    
    def _build_conflict_key(self, local: Local) -> str:
        """
        Build a normalized key used to detect possible duplicate Locals.

        The key combines normalized location_name, address and venue_type.
        """
        name_norm = normalize_text(local.name or "")
        # addr_norm = normalize_text(local.address or "") # TODO
        venue_norm = (
            normalize_text(local.venue_type.value) if local.venue_type is not None else ""
        )
        # return "|".join([name_norm, addr_norm, venue_norm]) # TODO
    
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
        criteria: ExternalLocalQueryCriteria,
    ) -> list[Local]:
        """
        Import Locals from the external Local API into the internal repository.

        Flow (to be implemented):
        - Build a payload with the given filters.
        - Call the external LocalInfo API.
        - For each result, map it to a Local entity.
        - Decide whether to:
            - create new Local (source=INTERNAL_SYNC),
            - update existing ones based on external_id,
            - or skip duplicates.
        - Return the list of persisted Local entities.
        
        Responsibilities:
        - Use `ExternalLocalQueryCriteria` to fetch venues from the external API.
        - Map them into domain `Local` instances.
        - Persist them via the Local repository, taking care to:
          * avoid duplicates (according to domain rules);
          * set proper `source` / `external_id`.

        Returns:
            List of `Local` entities that were actually imported.

        Raises:
            NotImplementedError: While the integration is not yet implemented.
        """
        payload = self._build_external_search_payload(criteria)

        logger.info("import_locals_from_external called but not implemented", payload=payload)

        raise NotImplementedError("External LocalInfo bulk import not implemented yet")

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