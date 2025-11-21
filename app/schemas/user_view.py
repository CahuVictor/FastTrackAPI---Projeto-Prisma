# app\schemas\user_view.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

class UserView(BaseModel):
    """
    Read-only representation of a user returned by the HTTP API.

    This schema is used as the response model for user endpoints.
    """
    
    id: int | None = Field(
        default=None,
        description="Unique identifier of the user in the database (if available).",
        examples=[1],
    )
    username: Annotated[str, Field(examples=["alice"])] = Field(
        description="Unique username used for login/identification.",
    )
    full_name: Annotated[str | None, Field(default=None)] = Field(
        description="Optional full name for display purposes.",
    )
    roles: Annotated[list[str], Field(default_factory=list)] = Field(
        description="List of roles assigned to the user. Example: ['admin', 'editor'].",
    )
    hashed_password: Annotated[str, Field(default="")] = Field(
        description="Hashed password (never return raw passwords).",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the user was created, if available.",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of the last update, if any.",
    )

    model_config = {
        # Allow building from domain/ORM objects with attribute access
        "from_attributes": True,
        "extra": "forbid",
    }