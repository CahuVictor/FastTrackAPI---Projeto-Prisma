# app\schemas\user_create.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated

class UserCreate(BaseModel):
    """
    Payload used to create a new user.

    This schema is received from the HTTP layer and then passed
    to the UserService, which handles validation and persistence.
    """

    username: Annotated[str, Field(examples=["alice"])] = Field(
        description="Unique username for login.",
    )
    full_name: Annotated[str | None, Field(default=None)] = Field(
        description="Optional full name.",
    )
    password: Annotated[str, Field()] = Field(
        description="Raw password. It will be hashed before storage.",
    )
    roles: Annotated[list[str], Field(default_factory=list)] = Field(
        description="List of roles assigned to the user.",
    )

    model_config = {
        "extra": "forbid",
    }