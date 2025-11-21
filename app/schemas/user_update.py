# app\schemas\user_update.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated

class UserUpdate(BaseModel):
    """
    Payload used to partially update a user.

    All fields are optional; only provided fields should be updated.
    """

    username: Annotated[str | None, Field(examples=["alice"])] = Field(
        default=None,
        description="New username. If omitted, the current one is kept.",
    )
    full_name: Annotated[str | None, Field(default=None)] = Field(
        description="Updated full name. If omitted, the current one is kept.",
    )
    password: Annotated[str | None, Field(default=None)] = Field(
        description="New password. If omitted, the current one is kept.",
    )
    roles: Annotated[list[str] | None, Field(default=None)] = Field(
        description=(
            "Replaces the entire list of roles. "
            "If omitted, the current roles are kept."
        ),
    )

    model_config = {
        "extra": "forbid",
    }