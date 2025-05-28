from pydantic import BaseModel, Field
from typing import Annotated, Optional

class User(BaseModel):
    roles: Annotated[list[str], Field(default_factory=[])]
    username: Annotated[str, Field(examples=["alice"])]
    full_name: Annotated[str | None, Field(default=None)]

class UserInDB(User):
    hashed_password: str
