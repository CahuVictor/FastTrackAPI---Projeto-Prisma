# app/controllers/api/local_integration_controller_helpers.py
from __future__ import annotations

from app.models.local_external_query import ExternalLocalQueryCriteria
from app.schemas.local.local_external_search import ExternalLocalSearch
from app.schemas.local.local_external_import import ExternalLocalImport


def from_external_local_search(schema: ExternalLocalSearch) -> ExternalLocalQueryCriteria:
    """
    Convert HTTP-level ExternalLocalSearch schema into the domain-level
    ExternalLocalQueryCriteria model.
    """
    data = schema.model_dump()
    return ExternalLocalQueryCriteria(**data)


def from_external_local_import(schema: ExternalLocalImport) -> ExternalLocalQueryCriteria:
    """
    Convert HTTP-level ExternalLocalImport schema into the domain-level
    ExternalLocalQueryCriteria model.

    For imports, `skip` is intentionally left as None, while `limit`
    controls the maximum number of venues to import.
    """
    data = schema.model_dump()
    return ExternalLocalQueryCriteria(**data)
