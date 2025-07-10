# app/db/base.py
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()  TODO verificar se alteração funciona
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase # type: ignore[attr-defined]

class Base(DeclarativeBase):
    """Classe‐raiz de todos os modelos ORM."""
    pass