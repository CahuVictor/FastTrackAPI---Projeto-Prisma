from pydantic import BaseModel, Field
from typing import Annotated, Optional

class User(BaseModel):
    username: str
    full_name: str | None = None
    roles: list[str] = [] 

class UserInDB(User):
    hashed_password: str
