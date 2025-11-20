# app/schemas/local_merge_request.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List


class LocalMergeRequest(BaseModel):
    target_id: int = Field(..., description="ID of the Local that will remain")
    source_ids: List[int] = Field(
        ..., description="IDs of Locals that will be merged into the target"
    )
