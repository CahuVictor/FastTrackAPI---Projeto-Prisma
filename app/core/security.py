from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=get_settings().auth_access_token_expire
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, get_settings().auth_secret_key, get_settings().auth_algorithm)
