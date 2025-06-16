# app/services/mock_users.py
from structlog import get_logger

from app.core.security import get_password_hash
from app.schemas.user import UserInDB
from app.services.interfaces.user_protocol import AbstractUserRepo

logger = get_logger().bind(module="mock_users")

class MockUserRepo(AbstractUserRepo):
    def __init__(self):
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
        self._users = {
            username: UserInDB(
                username=username,
                full_name=fullname,
                hashed_password=get_password_hash(raw_pwd),
                roles=roles,
            )
            for username, fullname, raw_pwd, roles in _RAW_USERS
        }

    def get_by_username(self, username: str) -> UserInDB | None:
        user = self._users.get(username)
        if user:
            logger.info("Usuário encontrado no mock", username=username)
        else:
            logger.warning("Usuário não encontrado no mock", username=username)
        return user
