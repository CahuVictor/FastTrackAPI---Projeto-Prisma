from app.core.security import get_password_hash
from app.schemas.user import UserInDB

# gere a hash só uma vez; na prática você faria isso num shell, não em runtime
_mock_users = {
    "alice": UserInDB(
        username="alice",
        full_name="Alice Liddell",
        hashed_password=get_password_hash("secret123")
    ),
    "bob": UserInDB(
        username="bob",
        full_name="Bob Builder",
        hashed_password=get_password_hash("builder123")
    ),
}

def get_user(username: str) -> UserInDB | None:
    return _mock_users.get(username)
