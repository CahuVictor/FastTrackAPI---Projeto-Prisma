# app/models/models_user.py
from sqlalchemy import Column, Integer, String

from app.infra.db.base import Base

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(String, nullable=False)  # armazenado como string separada por vírgula