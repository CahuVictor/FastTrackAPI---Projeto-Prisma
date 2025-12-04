# app/infra/repositories/inmemory/audit_repo_inmemory.py
from __future__ import annotations

from typing import Dict, List
from structlog import get_logger
from datetime import datetime

from app.models.audit_log_command import AuditLogCommand
from app.models.audit_filters import AuditFilterCriteria
from app.repositories.audit_repo import AuditRepository

logger = get_logger().bind(module="audit_repo_inmemory")


def _apply_filter_and_sort(
    logs_list: list[AuditLogCommand],
    *,
    filter: AuditFilterCriteria,
) -> list[AuditLogCommand]:
    """
    Apply the in-memory filtering and sorting logic over a list of Events.

    This helper keeps the `list` method smaller and centralizes all
    filter conditions in one place. It also documents the fact that,
    in this in-memory implementation, all data is loaded into memory
    before applying filters — which is different from a future SQL
    implementation, where filters should be translated to WHERE clauses.
    """
    return logs_list

    # # -------------------------
    # # Core content filters
    # # -------------------------
    # if filter.title is not None:
    #     if isinstance(filter.title, list):
    #         needles = [t.lower() for t in filter.title]
    #         events_list = [
    #             e
    #             for e in events_list
    #             if any(n in e.title.lower() for n in needles)
    #         ]
    #     else:
    #         needle = filter.title.lower()
    #         events_list = [e for e in events_list if needle in e.title.lower()]

    # if filter.description is not None:
    #     if isinstance(filter.description, list):
    #         needles = [d.lower() for d in filter.description]
    #         events_list = [
    #             e
    #             for e in events_list
    #             if any(
    #                 n in (e.description or "").lower()
    #                 for n in needles
    #             )
    #         ]
    #     else:
    #         needle = filter.description.lower()
    #         events_list = [
    #             e
    #             for e in events_list
    #             if e.description and needle in e.description.lower()
    #         ]

    # if filter.status is not None:
    #     if isinstance(filter.status, list):
    #         allowed = set(filter.status)
    #         events_list = [e for e in events_list if e.status in allowed]
    #     else:
    #         events_list = [e for e in events_list if e.status == filter.status]

    # # -------------------------
    # # Scheduling filters
    # # -------------------------
    # if filter.start_from is not None:
    #     events_list = [
    #         e for e in events_list if e.start_time >= filter.start_from
    #     ]

    # if filter.start_to is not None:
    #     events_list = [
    #         e for e in events_list if e.start_time <= filter.start_to
    #     ]

    # # -------------------------
    # # Context / classification
    # # -------------------------
    # if filter.city is not None:
    #     needle = filter.city.lower()
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.city is not None and needle in e.city.lower()
    #     ]

    # if filter.age_restriction is not None:
    #     if isinstance(filter.age_restriction, list):
    #         allowed = {a.lower() for a in filter.age_restriction}
    #         events_list = [
    #             e
    #             for e in events_list
    #             if e.age_restriction and e.age_restriction.lower() in allowed
    #         ]
    #     else:
    #         needle = filter.age_restriction.lower()
    #         events_list = [
    #             e
    #             for e in events_list
    #             if e.age_restriction and e.age_restriction.lower() == needle
    #         ]

    # if filter.expected_audience is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.expected_audience == filter.expected_audience
    #     ]

    # if filter.environment is not None:
    #     if isinstance(filter.environment, list):
    #         allowed = set(filter.environment)
    #         events_list = [e for e in events_list if e.environment in allowed]
    #     else:
    #         events_list = [
    #             e for e in events_list if e.environment == filter.environment
    #         ]

    # # -------------------------
    # # Engagement filters
    # # -------------------------
    # if filter.participants is not None:
    #     if isinstance(filter.participants, list):
    #         needles = [p.lower() for p in filter.participants]
    #         events_list = [
    #             e
    #             for e in events_list
    #             if any(
    #                 p.lower() in [ep.lower() for ep in e.participants]
    #                 for p in needles
    #             )
    #         ]
    #     else:
    #         needle = filter.participants.lower()
    #         events_list = [
    #             e
    #             for e in events_list
    #             if any(needle == p.lower() for p in e.participants)
    #         ]

    # if filter.views_min is not None:
    #     events_list = [
    #         e for e in events_list if e.views >= filter.views_min
    #     ]

    # if filter.views_max is not None:
    #     events_list = [
    #         e for e in events_list if e.views <= filter.views_max
    #     ]

    # # -------------------------
    # # Audit filters
    # # -------------------------
    # if filter.created_from is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.created_at is not None and e.created_at >= filter.created_from
    #     ]

    # if filter.created_to is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.created_at is not None and e.created_at <= filter.created_to
    #     ]

    # if filter.updated_from is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.updated_at is not None and e.updated_at >= filter.updated_from
    #     ]

    # if filter.updated_to is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.updated_at is not None and e.updated_at <= filter.updated_to
    #     ]

    # if filter.deleted_from is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.deleted_at is not None and e.deleted_at >= filter.deleted_from
    #     ]

    # if filter.deleted_to is not None:
    #     events_list = [
    #         e
    #         for e in events_list
    #         if e.deleted_at is not None and e.deleted_at <= filter.deleted_to
    #     ]

    # # created_by / updated_by / deleted_by como igualdade simples ou lista
    # def _match_str_field(value: str | None, criterion: list[str] | str | None) -> bool:
    #     if criterion is None:
    #         return True
    #     if value is None:
    #         return False
    #     if isinstance(criterion, list):
    #         allowed = {c.lower() for c in criterion}
    #         return value.lower() in allowed
    #     return value.lower() == criterion.lower()

    # events_list = [
    #     e
    #     for e in events_list
    #     if _match_str_field(e.created_by, filter.created_by)
    # ]
    # events_list = [
    #     e
    #     for e in events_list
    #     if _match_str_field(e.updated_by, filter.updated_by)
    # ]
    # events_list = [
    #     e
    #     for e in events_list
    #     if _match_str_field(e.deleted_by, filter.deleted_by)
    # ]

    # # -------------------------
    # # Sorting & pagination
    # # -------------------------
    # # Deterministic ordering: by start_time then id
    # events_list.sort(key=lambda e: (e.start_time, e.id or 0))

    # # Pagination
    # if filter.skip:
    #     events_list = events_list[filter.skip :]

    # if filter.limit and filter.limit > 0:
    #     events_list = events_list[: filter.limit]

    # return events_list


class AuditRepoInMemory(AuditRepository):
    """
    In-memory implementation of AuditRepository.

    This repository is useful for:
    - unit tests (no database required);
    - local development where audit persistence is not critical;
    - prototyping features before wiring SQLAlchemy.

    The storage is **process-local** and will be lost when the app restarts.

    Even though the underlying table is generic (audit_logs), this
    implementation still provides `list_by_event` for backwards
    compatibility with the current AuditService, interpreting
    "event" as entity_name == 'events'.
    """

    def __init__(self) -> None:
        # simple in-memory store: audit_id -> AuditLogTable-like object
        self._storage: Dict[int, AuditLogCommand] = {}
        self._next_id: int = 1

        logger.debug("AuditRepoInMemory initialized")

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    def _generate_id(self) -> int:
        """
        Generate a new incremental identifier for audit records.

        Returns:
            Integer ID that is unique within this in-memory repository.
        """
        new_id = self._next_id
        self._next_id += 1
        return new_id

    # ------------------------------------------------------------------ #
    # CREATE                                                             #
    # ------------------------------------------------------------------ #
    def add(self, audit: AuditLogCommand) -> AuditLogCommand:
        """
        Store a new audit log entry in memory.

        Args:
            audit:
                AuditLogCommand instance to be stored. The `id` will be
                assigned by this repository if it is None.

        Returns:
            The same instance with `id` filled.
        """
        if audit.id is None:
            audit.id = self._generate_id()
        
        now = datetime.utcnow()
        audit.changed_at = now

        self._storage[audit.id] = audit

        logger.info(
            "Audit entry stored in memory",
            audit_id=audit.id,
            entity_name=getattr(audit, "entity_name", None),
            row_id=getattr(audit, "row_id", None),
            action=getattr(audit, "action", None),
            changed_by_user_id=getattr(audit, "changed_by_user_id", None),
        )

        return audit

    # ------------------------------------------------------------------ #
    # READ                                                              #
    # ------------------------------------------------------------------ #
    def list_by_event(self, event_id: int) -> List[AuditLogCommand]:
        """
        Return all audit log entries for a given Event.

        This method is kept for backwards compatibility with the
        event-centric use case. It is implemented as:

            entity_name == 'events' AND row_id == event_id

        Args:
            event_id:
                ID of the event whose audit trail should be fetched.

        Returns:
            List of AuditLogCommand entries ordered by `changed_at`
            ascending.
        """
        logs = [
            a
            for a in self._storage.values()
            if getattr(a, "entity_name", None) == "events"
            and getattr(a, "row_id", None) == event_id
        ]
        logs.sort(key=lambda a: a.changed_at)

        logger.info(
            "Audit logs fetched from memory by event",
            event_id=event_id,
            total=len(logs),
        )
        return logs

    # ----------------------------------------------------------------------
    # LIST
    # ----------------------------------------------------------------------
    def list(
        self,
        *,
        filter: AuditFilterCriteria | None = None,
    ) -> list[AuditLogCommand]:
        """
        ???
        """
        logs = list(self._storage.values())

        if filter is not None:
            logs_list = _apply_filter_and_sort(logs, filter=filter)

            logger.info(
                "??",
                total=len(logs_list),
                filter=filter,
            )

            return logs_list
        
        return logs

    def list_recent(self, limit: int = 50) -> List[AuditLogCommand]:
        """
        Return the most recent audit log entries across all entities.

        Args:
            limit:
                Maximum number of records to return. If <= 0, a default
                of 50 is used.

        Returns:
            List of AuditLogCommand entries ordered by `changed_at`
            descending (most recent first).
        """
        if limit <= 0:
            limit = 50

        logs = list(self._storage.values())
        logs.sort(key=lambda a: a.changed_at, reverse=True)

        selected = logs[:limit]

        logger.info(
            "Recent audit entries fetched from memory",
            total=len(selected),
            limit=limit,
        )
        return selected

	# # Opcional: helper para testes
    # def clear(self) -> None:
    #     """
    #     Clear all stored audit records (mainly for testing purposes).
    #     """
    #     self._storage.clear()
    #     self._next_id = 1
    #     logger.info("All in-memory event audit logs have been cleared")
