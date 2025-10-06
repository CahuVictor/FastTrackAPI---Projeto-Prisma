# app/services/user_db.py
from sqlalchemy.orm import Session
from app.schemas.user import UserInDB
from app.services.interfaces.user_protocol import AbstractUserRepo
from app.models.models_user import User  # supondo que você terá um modelo SQLAlchemy

class UserRepo(AbstractUserRepo):
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> UserInDB | None:
        db_user = self.db.query(User).filter_by(username=username).first()
        if not db_user:
            return None
        return UserInDB.model_validate(db_user)
