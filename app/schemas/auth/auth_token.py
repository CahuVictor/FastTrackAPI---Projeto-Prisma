# app/schemas/auth_token.py
from __future__ import annotations

from pydantic import BaseModel, Field


class AuthToken(BaseModel):
    """
    Response payload for authentication operations.

    This model is returned after a successful login or token refresh.
    """

    access_token: str = Field(
        description="JWT access token used to authenticate protected requests.",
    )
    token_type: str = Field(
        default="bearer",
        description="Type of the token. Usually 'bearer'.",
    )
    # expires_in: int = Field(
    #     description="Number of seconds before the access token expires.",
    #     examples=[900],
    # )
    refresh_token: str | None = Field(
        default=None,
        description="Optional refresh token used to obtain a new access token.",
    )

    model_config = {
        "extra": "forbid",
    }
