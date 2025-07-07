# app/repositories/user_mem.py
from structlog import get_logger
from app.schemas.user import UserInDB
from app.repositories.user import AbstractUserRepo

from app.core.security import get_password_hash

logger = get_logger().bind(module="user_mem")

class InMemoryUserRepo(AbstractUserRepo):
    def __init__(self):
        # self._db: dict[str, UserInDB] = {}
        
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
        self._db = {
            username: UserInDB(
                username=username,
                full_name=fullname,
                hashed_password=get_password_hash(raw_pwd),
                roles=roles,
            )
            for username, fullname, raw_pwd, roles in _RAW_USERS
        }

    def get_by_username(self, username: str) -> UserInDB | None:
        logger.debug("Buscando usuário por username", username=username)
        return self._db.get(username)

    def list_all(self) -> list[UserInDB]:
        logger.info("Listando todos os usuários", total=len(self._db))
        return list(self._db.values())

    def add(self, user: UserInDB) -> UserInDB:
        logger.info("Adicionando novo usuário", username=user.username)
        self._db[user.username] = user
        return user

    def delete_by_username(self, username: str) -> bool:
        if username in self._db:
            logger.info("Removendo usuário", username=username)
            del self._db[username]
            return True
        logger.warning("Usuário não encontrado para remoção", username=username)
        return False
