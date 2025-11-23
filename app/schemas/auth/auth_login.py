# app/schemas/auth_login.py
from __future__ import annotations

from pydantic import BaseModel, Field


class AuthLogin(BaseModel):
    """
    Request payload for user login.

    Carries the raw credentials that will be validated by the AuthService.
    """

    username: str = Field(
        description="Unique username for login.",
        examples=["alice"],
    )
    password: str = Field(
        description="Raw password. It will be validated and never stored in plain form.",
        examples=["secret123"],
    )

    model_config = {
        "extra": "forbid",
    }
