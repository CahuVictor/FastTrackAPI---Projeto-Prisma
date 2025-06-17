from pydantic import BaseModel, Field
from typing import Annotated
from typing import Any
from datetime import datetime
from app.schemas.weather_forecast import WeatherForecast
from app.schemas.local_info import LocalInfo

from pydantic import field_validator

class EventCreate(BaseModel):
    @field_validator("title", "description", mode="before")
    @classmethod
    def limpar_texto(cls, v):
        return v.strip().title() if isinstance(v, str) else v

    title: Annotated[str, Field(max_length=100, description="Título do evento", json_schema_extra={"example": "Festival de Tecnologia"})]
    description: Annotated[str, Field(description="Descrição detalhada", json_schema_extra={"example": "Evento com oficinas, palestras e música."})]
    event_date: Annotated[datetime, Field(description="Data e hora do evento", json_schema_extra={"example": "2025-06-12T19:00:00"})]
    city: Annotated[str, Field(description="Cidade onde o evento ocorrerá", json_schema_extra={"example": "Recife"})]
    participants: Annotated[list[str], Field(description="Lista de participantes", json_schema_extra={"example": ["Alice", "Bob", "Carol"]})]
    local_info: LocalInfo               # local_info: LocalInfo | None = None # obsoleto Optional[dict]
    
    # ----------------------------------------------
    #  Permite EventCreate(...) nos testes unitários
    # ----------------------------------------------
    def __init__(self, *args: Any, **data: Any) -> None:  # type: ignore[override]
        if args and args[0] is ... and not data:
            data = _make_dummy_event_data()
        
        if "local_info" not in data:
            data["local_info"] = _make_default_local_info()
            
        super().__init__(**data)

def _make_default_local_info() -> LocalInfo:
    return LocalInfo(
        location_name="local",
        capacity=1,
        venue_type=None,
        is_accessible=False,
        address=None,
        past_events=[],
        manually_edited=False,
    )


def _make_dummy_event_data() -> dict[str, Any]:
    return dict(
        title="Evento genérico",
        description="Descrição genérica",
        event_date=datetime.utcnow(),
        city="Recife",
        participants=[],
        local_info=_make_default_local_info(),
    )
 
class EventResponse(EventCreate):
    id: int
    forecast_info: WeatherForecast | None = None
    views: int = 0 # (default = 0)
    