# app/schemas/common/pagination_filters.py
from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel, Field

class PaginationFilters(BaseModel):
    skip: Annotated[int, Field(
        ge=0,
        default=0,
        description="How many records to skip (offset).",
    )]
    limit: Annotated[int, Field(
        ge=1,
        le=200,
        default=50,
        description="Maximum number of records to return.",
    )]