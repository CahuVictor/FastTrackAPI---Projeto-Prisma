# app/models/audit_filters.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.enums import AuditAction, AuditEntityName


@dataclass(slots=True)
class AuditFilterCriteria:
    """
    Domain-level filter model for audit entries.

    Although originally designed for event audit logs, this model is
    generic enough to represent filters for any audited entity.

    It is used by the service layer and can be translated to/from
    HTTP-level schemas or repository-specific filter mechanisms.
    """

    skip: int = 0
    limit: int = 20

    # Generic “what was audited”
    entity_name: AuditEntityName | None = None
    row_id: int | None = None

    # Metadata
    action: AuditAction | None = None
    changed_by_user_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None