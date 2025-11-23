# app/schemas/auth_me_view.py
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class AuthMeView(BaseModel):
    """
    Lightweight representation of the currently authenticated user.

    This schema is used by the `/auth/me` endpoint and intentionally
    does not expose sensitive fields such as `hashed_password`.
    """

    id: int | None = Field(
        default=None,
        description="Internal identifier of the user (if available).",
        examples=[1],
    )
    username: Annotated[str, Field(examples=["alice"])] = Field(
        description="Unique username used for login.",
    )
    full_name: Annotated[str | None, Field(default=None)] = Field(
        description="Optional full name for display.",
    )
    roles: list[str] = Field(
        default_factory=list,
        description="List of roles assigned to the user.",
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }
