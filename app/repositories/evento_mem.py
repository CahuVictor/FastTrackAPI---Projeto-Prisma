# app/repositories/evento_mem.py
from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.weather_forecast import WeatherForecast
from app.schemas.local_info import LocalInfo
from app.repositories.evento import AbstractEventoRepo

class InMemoryEventoRepo(AbstractEventoRepo):
    def __init__(self):
        self._db: dict[int, EventResponse] = {}
        self._id_counter = 1

    def list_all(self) -> list[EventResponse]:
        return list(self._db.values())

    def list_partial(self, *, skip: int = 0, limit: int = 20, city: str | None = None):
        data = list(self._db.values())
        if city:
            data = [e for e in data if e.city.lower() == city.lower()]
        return data[skip : skip + limit]

    def get(self, evento_id: int) -> EventResponse | None:
        return self._db.get(evento_id)

    def add(self, evento: EventCreate) -> EventResponse:
        evento_resp = EventResponse(
            id=self._id_counter,
            title=evento.title,
            description=evento.description,
            event_date=evento.event_date,
            city=evento.city,
            participants=evento.participants,
            local_info=evento.local_info,
            forecast_info=None  # será setado depois se necessário
        )
        self._db[self._id_counter] = evento_resp
        self._id_counter += 1
        return evento_resp

    def replace_all(self, eventos: list[EventResponse]) -> list[EventResponse]:
        self._db = {e.id: e for e in eventos}
        return list(self._db.values())

    def replace_by_id(self, evento_id: int, evento: EventResponse) -> EventResponse:
        self._db[evento_id] = evento
        return evento

    def delete_all(self) -> None:
        self._db.clear()

    def delete_by_id(self, evento_id: int) -> bool:
        return self._db.pop(evento_id, None) is not None

    def update(self, evento_id: int, data: dict) -> EventResponse:
        existing = self._db.get(evento_id)
        if not existing:
            raise ValueError("Evento não encontrado")
        for key, value in data.items():
            setattr(existing, key, value)
        self._db[evento_id] = existing
        return existing
