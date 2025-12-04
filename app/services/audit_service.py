# app/services/audit_service.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List

from structlog import get_logger

from app.models.audit_filters import AuditFilterCriteria
from app.models.audit_log_input import AuditLogInput
from app.models.audit_log_command import AuditLogCommand
from app.models.enums import AuditAction
from app.repositories.audit_repo import AuditRepository

logger = get_logger().bind(module="audit_service")


class AuditService:
    """
    Application service responsible for handling audit-related use cases
    for *any* entity in the system.

    It encapsulates how audit records are created and retrieved, and
    provides dedicated helper methods for common actions (created,
    updated, deleted, restored), plus query helpers used by the HTTP
    layer (controllers).
    """

    def __init__(self, repo: AuditRepository) -> None:
        """
        Initialize the service with a concrete AuditRepository.

        Args:
            repo:
                Concrete implementation of the audit repository, such as a
                SQLAlchemy-based repository or an in-memory version for tests.
        """
        self.repo = repo


    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _make_command(self, *, base: AuditLogInput, action: AuditAction) -> AuditLogCommand:
        """
        Build an `AuditLogCommand` from a generic `AuditLogInput` plus
        a specific `AuditAction`.
        """
        return AuditLogCommand(
            entity_name=base.entity_name,
            row_id=base.row_id,
            action=action,
            changed_by_user_id=base.changed_by_user_id,
            changes=base.changes,
            snapshot=base.snapshot,
            reason=base.reason,
            ip_address=base.ip_address,
            changed_at=base.changed_at,
        )

    # def _command_to_table(self, cmd: AuditLogCommand) -> AuditLogCommand:
    #     """
    #     Convert an `AuditLogCommand` into an `AuditLogCommand` instance,
    #     applying default values such as `changed_at` (UTC now).
    #     """
    #     effective_changed_at = cmd.changed_at or datetime.utcnow()

    #     audit = AuditLogCommand(
    #         entity_name=cmd.entity_name,
    #         row_id=cmd.row_id,
    #         action=cmd.action,
    #         changed_at=effective_changed_at,
    #         changed_by_user_id=cmd.changed_by_user_id,
    #         reason=cmd.reason,
    #         ip_address=cmd.ip_address,
    #         changes=cmd.changes,
    #         snapshot=cmd.snapshot,
    #     )

    #     return audit


    # ------------------------------------------------------------------ #
    # Core logging method                                                #
    # ------------------------------------------------------------------ #
    def log_action(
        self,
        # *,
        command: AuditLogCommand,
    ) -> AuditLogCommand:
        """
        Persist a generic audit log entry for the given entity row.
        
        The public helpers (`log_created`, `log_updated`, etc.) should
        build an `AuditLogInput`, convert it into an `AuditLogCommand`
        with the appropriate `AuditAction`, and then call this method.

        Args:
            entity_name:
                Logical name of the audited table/entity
                (e.g. "events", "users", "locals").
            row_id:
                Primary key value of the audited row in the origin table.
            action:
                High-level action type
                (created, updated, deleted, soft_deleted, restored).
            changed_by_user_id:
                ID of the user that performed the action (User.id), or None
                when the change is system-driven.
            changes:
                Optional diff-like structure describing what changed.
            snapshot:
                Optional snapshot of the current row state after the change.
            reason:
                Optional human-readable explanation for the change.
            ip_address:
                Optional IP address where the change was triggered from.
            changed_at:
                Timestamp of the change; defaults to now (UTC) if not provided.

        Returns:
            The persisted `AuditLogCommand` instance.
        """
        # audit = self._command_to_table(command)
        saved = self.repo.add(command) # (audit)

        logger.info(
            "Audit log recorded",
            audit_id=saved.id,
            entity_name=saved.entity_name,
            row_id=saved.row_id,
            action=saved.action.value,
            changed_by_user_id=saved.changed_by_user_id,
        )
        return saved

    # ------------------------------------------------------------------ #
    # Helper methods for common actions                                  #
    # ------------------------------------------------------------------ #
    def log_created(
        self,
        # *,
        base: AuditLogInput,
    ) -> AuditLogCommand:
        """
        Shortcut to register a 'created' audit entry for the given row.
        """
        cmd = self._make_command(base=base, action=AuditAction.CREATED)
        return self.log_action(cmd)

    def log_updated(
        self,
        # *,
        base: AuditLogInput,
    ) -> AuditLogCommand:
        """
        Shortcut to register an 'updated' audit entry.
        
        `base.changes` should contain a diff structure describing which
        fields changed and how.

        Args:
            entity_name:
                Name of the audited entity/table.
            row_id:
                Primary key of the audited row.
            changed_by_user_id:
                User responsible for the change.
            changes:
                Dict describing which fields changed and how, e.g.:

                {
                    "status": {"old": "draft", "new": "published"},
                    "expected_audience": {"old": 100, "new": 300}
                }
        """
        cmd = self._make_command(base=base, action=AuditAction.UPDATED)
        return self.log_action(cmd)

    def log_deleted(
        self,
        # *,
        base: AuditLogInput,
    ) -> AuditLogCommand:
        """
        Shortcut to register a 'deleted' (hard delete) audit entry.
        """
        cmd = self._make_command(base=base, action=AuditAction.DELETED)
        return self.log_action(cmd)

    def log_soft_deleted(
        self,
        # *,
        base: AuditLogInput,
    ) -> AuditLogCommand:
        """
        Shortcut to register a 'soft_deleted' audit entry.
        """
        cmd = self._make_command(base=base, action=AuditAction.SOFT_DELETED)
        return self.log_action(cmd)

    def log_restored(
        self,
        # *,
        base: AuditLogInput,
    ) -> AuditLogCommand:
        """
        Shortcut to register a 'restored' audit entry (undo soft-delete).
        """
        cmd = self._make_command(base=base, action=AuditAction.RESTORED)
        return self.log_action(cmd)

    # ------------------------------------------------------------------ #
    # Query helpers (used by controllers)                                #
    # ------------------------------------------------------------------ #

    def _matches_filters(self, log: AuditLogCommand, filters: AuditFilterCriteria) -> bool:
        """
        Check whether a given `AuditLogCommand` entry matches the provided
        `AuditFilterCriteria`.
        """
        # entity_name
        if filters.entity_name is not None and log.entity_name != filters.entity_name:
            return False

        # row id
        if filters.row_id is not None and log.row_id != filters.row_id:
            return False

        # action
        if filters.action is not None and log.action != filters.action:
            return False

        # changed_by_user_id
        if (
            filters.changed_by_user_id is not None
            and log.changed_by_user_id != filters.changed_by_user_id
        ):
            return False

        # date range
        if filters.date_from is not None and log.changed_at < filters.date_from:
            return False
        if filters.date_to is not None and log.changed_at > filters.date_to:
            return False

        return True

    @staticmethod
    def _apply_pagination(
        items: List[AuditLogCommand],
        *,
        skip: int | None,
        limit: int | None,
    ) -> List[AuditLogCommand]:
        """
        Apply the common pagination rules used across the project:
        - `skip` default = 0
        - `limit` default = 0 (means "no limit")
        """
        s = skip or 0
        l = limit or 0

        if l > 0:
            return items[s : s + l]
        return items[s:]

    def list_logs(
        self,
        *,
        filters: AuditFilterCriteria,
    ) -> List[AuditLogCommand]:
        """
        List audit logs with optional filters and pagination.

        All filters are optional and combined using AND semantics.

        Args:
            filters:
                Domain-level filter criteria including pagination
                (skip, limit) and optional fields:
                - entity_name
                - row_id
                - action (AuditAction)
                - changed_by_user_id
                - date_from (inclusive, UTC)
                - date_to   (inclusive, UTC)

        Returns:
            A list of audit entries that match the filters, sliced
            according to `filters.skip` and `filters.limit`.

        Notes:
            For now, this implementation loads all records from the
            repository and applies filtering in Python. When a SQL-backed
            repository is in use, this logic can be pushed down to SQL.
        """
        logs = self.repo.list(filter=filters)

        logger.info(
            "Audit logs filtered",
            total=len(logs),
            filters=filters,
        )

        return logs

    def list_recent(self, limit: int = 50) -> List[AuditLogCommand]:
        """
        Return the most recent audit entries across all entities.

        Args:
            limit:
                Maximum number of records to return.

        Returns:
            A list of `AuditLogCommand` ordered by recency.
        """
        logs = self.repo.list_recent(limit=limit)
        logger.info("Recent audit logs fetched", total=len(logs), limit=limit)
        return logs

    # ------------------------------------------------------------------ #
    # Event-centric compatibility helpers                                #
    # ------------------------------------------------------------------ #
    
    def list_by_event(self, event_id: int) -> List[AuditLogCommand]:
        """
        Convenience wrapper to fetch audit logs for the 'events' entity.

        Equivalent to:
            entity_name == 'events' AND row_id == event_id

        Args:
            event_id:
                ID of the Event whose audit logs should be returned.

        Returns:
            A list of `AuditLogCommand` ordered according to repository
            implementation (typically by `changed_at` ascending or descending).
        """
        criteria = AuditFilterCriteria(
            skip=0,
            limit=0,
            entity_name="events",
            row_id=event_id,
        )
        return self.list_logs(filters=criteria)

    def list_for_event(
        self,
        event_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AuditLogCommand]:
        """
        Return the audit trail for a given Event, with simple pagination.

        Args:
            event_id:
                ID of the Event whose audit logs should be returned.
            skip:
                How many records to skip (offset).
            limit:
                Maximum number of records to return.

        Returns:
            A list of `AuditLogCommand` entries ordered by `changed_at`
            according to the repository implementation.
            
        Convenience wrapper to fetch paginated audit logs for the
        'events' entity.
        """
        
        criteria = AuditFilterCriteria(
            skip=skip,
            limit=limit,
            entity_name="events",
            row_id=event_id,
        )
        logs = self.list_logs(filters=criteria)
        
        logger.info(
            "Audit logs fetched for single event",
            total=len(logs),
            filters=criteria,
        )
        
        return logs

    def list_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        action: AuditAction | None = None,
        changed_by: int | None = None,
    ) -> List[AuditLogCommand]:
        """
        List all logs, optionally filtering by action or user.

        This method is mainly used by legacy or simpler endpoints that
        don't require the full filter DTO.

        Args:
            skip:
                How many records to skip (offset).
            limit:
                Maximum number of records to return.
            action:
                Optional filter by action enum.
            changed_by:
                Optional substring filter by `changed_by`.

        Returns:
            A paginated list of audit entries.
        """
        logs = self.repo.list_all()

        def _match(log: AuditLogCommand) -> bool:
            if action and log.action != action:
                return False
            # TODO adicionar o filtro changed_by
            # if changed_by and changed_by.lower() not in (log.changed_by or "").lower():
            #     return False
            return True

        filtered = [log for log in logs if _match(log)]
        sliced = filtered[skip : skip + limit]

        logger.info(
            "Audit logs fetched (all)",
            total=len(filtered),
            returned=len(sliced),
            skip=skip,
            limit=limit,
            action=action.value if action else None,
            changed_by=changed_by,
        )

        return sliced
