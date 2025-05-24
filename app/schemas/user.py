from pydantic import BaseModel, Field
from typing import Annotated, Optional

class User(BaseModel):
    username: Annotated[str, Field(examples=["alice"])]
    full_name: Annotated[str | None, Field(default=None)]

class UserInDB(User):
    hashed_password: str
