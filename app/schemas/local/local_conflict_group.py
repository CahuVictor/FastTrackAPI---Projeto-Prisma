# app/schemas/local_conflict_group.py
from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.schemas.local.local_view import LocalView


class LocalConflictGroup(BaseModel):
    conflict_key: str
    locals: List[LocalView]
