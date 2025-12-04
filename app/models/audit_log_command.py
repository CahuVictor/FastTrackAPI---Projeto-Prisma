# app/models/audit_log_command.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models.enums import AuditAction, AuditEntityName

# ---------------------------------------------------------------------- #
# Command/DTO classes for logging                                        #
# ---------------------------------------------------------------------- #

@dataclass(slots=True)
class AuditLogCommand:
    """
    Internal command used by `log_action`, already including the action.

    This is the structure that will be converted to `AuditLogTable`.
    """
    
    # obrigatórios (sem default) – PRECISAM vir primeiro
    entity_name: AuditEntityName
    row_id: int
    action: AuditAction
    
    # opcionais (com default)
    changed_by_user_id: int | None
    changes: dict[str, Any] | None = None
    snapshot: dict[str, Any] | None = None
    reason: str | None = None
    ip_address: str | None = None
    changed_at: datetime | None = None
    id: int | None = None  # se quiser guardar o id já atribuído pelo repo (opcional)