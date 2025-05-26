from app.core.security import get_password_hash
from app.schemas.user import UserInDB

_RAW_USERS = [
    # username  full name           password      roles
    ("alice",   "Alice Liddell",    "secret123",  ["admin"]),
    ("bob",     "Bob Builder",      "builder123", ["editor"]),
    ("carol",   "Carol Jones",      "pass123",    ["viewer"]),
    ("dave",    "Dave Stone",       "pass123",    ["viewer"]),
    ("eve",     "Eve Adams",        "pass123",    ["editor"]),
    ("frank",   "Frank Wright",     "pass123",    ["editor"]),
    ("grace",   "Grace Kim",        "pass123",    ["viewer"]),
    ("heidi",   "Heidi Cruz",       "pass123",    ["viewer"]),
    ("ivan",    "Ivan Lee",         "pass123",    ["viewer"]),
    ("judy",    "Judy Moe",         "pass123",    ["viewer"]),
]

_mock_users: dict[str, UserInDB] = {}

for username, fullname, raw_pwd, roles in _RAW_USERS:
    _mock_users[username] = UserInDB(
        username=username,
        full_name=fullname,
        hashed_password=get_password_hash(raw_pwd),
        roles=roles,                 # novo campo
    )

def get_user(username: str) -> UserInDB | None:
    return _mock_users.get(username)
