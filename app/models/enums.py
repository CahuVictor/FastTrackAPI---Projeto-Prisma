# app/models/event_local_enums.py
from enum import Enum


class EventStatus(str, Enum):
    """
    Lifecycle status for an Event.

    Values:
        DRAFT:
            The event is being prepared and is not visible to the public yet.
        PUBLISHED:
            The event is active and visible to users.
        CANCELLED:
            The event was created but later cancelled.
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class LocalSource(str, Enum):
    """
    Describes where the Local (venue) data comes from and how it should be managed.

    Values:
        INTERNAL_SYNC:
            The venue is fully managed and synchronized by an internal API
            (e.g. LocalInfo service). Manual changes should be avoided.
        MANUAL:
            The venue was created and is maintained manually inside this service.
            Automatic sync should never overwrite it blindly.
        MIXED:
            The venue was originally imported or synced from an external source,
            but important fields were manually overridden and must be preserved.
    """
    INTERNAL_SYNC = "internal_sync"
    MANUAL = "manual"
    MIXED = "mixed"


class VenueType(str, Enum):
    """
    High-level classification of the physical (or virtual) venue type.

    Values:
        AUDITORIO:
            Auditorium style venue (usually seated, indoor).
        SALAO:
            Large multi-purpose room or ballroom.
        THEATER:
            Theater-style venue, stage + audience.
        STADIUM:
            Large open/semiclosed stadium, typically for sports/shows.
        HALL:
            Generic hall, lobby or event hall.
        OPEN_AIR:
            Open-air venue, usually outdoor without full coverage.
    """
    AUDITORIO = "Auditorio"
    SALAO = "Salao"
    THEATER = "theater"
    STADIUM = "stadium"
    HALL = "hall"
    OPEN_AIR = "open_air"

class EventEnvironment(str, Enum):
    """
    Constraints about where the event must take place in terms of
    indoor/outdoor requirements.

    Values:
        INDOOR:
            Event must be held indoors (covered, controlled environment).
        OUTDOOR:
            Event must be held outdoors.
        HYBRID:
            Event can mix indoor and outdoor segments by design.
        UNRESTRICTED:
            No specific constraint; indoor or outdoor is acceptable.
    """
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    HYBRID = "hybrid"
    UNRESTRICTED = "unrestricted"

class AuditAction(str, Enum):
    """
    Allowed action types for audit entries.

    Values:
        CREATED:
            A new row was inserted.
        UPDATED:
            An existing row was modified.
        DELETED:
            A row was hard-deleted (physically removed).
        SOFT_DELETED:
            A row was logically deleted (soft delete flag set).
        RESTORED:
            A previously soft-deleted row was restored.
    """

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    SOFT_DELETED = "soft_deleted"
    RESTORED = "restored"

class AuditEntityName(str, Enum):
    """
    Lista controlada de entidades/tabelas que podem gerar logs de auditoria.

    Usamos string Enum para:
    - evitar erros de digitação em 'entity_name';
    - manter compatibilidade com JSON / Pydantic / banco.

    Adicione novos valores conforme forem surgindo novas tabelas auditadas.
    """
    EVENTS = "events"
    USERS = "users"
    LOCALS = "locals"

    # Exemplo de expansão futura:
    # FORECASTS = "forecasts"
    # ASSOCIATIONS = "associations"
    # RESPONSIBLES = "responsibles"

class AgeRestriction(str, Enum):
    LIVRE = "Livre"
    TEN = "10+"
    TWELVE = "12+"
    FOURTEEN = "14+"
    SIXTEEN = "16+"
    EIGHTEEN = "18+"
