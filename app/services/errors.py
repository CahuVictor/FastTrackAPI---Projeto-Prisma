# app/services/local_service.py
from __future__ import annotations

class DuplicateLocalError(Exception):
    """Raised when attempting to create or update a Local that already exists
    with the same normalized (location_name, venue_type, address)."""
    pass