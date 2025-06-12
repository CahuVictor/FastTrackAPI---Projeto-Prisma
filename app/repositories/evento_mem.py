# app/repositories/evento_mem.py
from app.schemas.event_create import EventCreate, EventResponse
# from app.schemas.weather_forecast import WeatherForecast
# from app.schemas.local_info import LocalInfo
from app.repositories.evento import AbstractEventoRepo

class InMemoryEventoRepo(AbstractEventoRepo):
    def __init__(self):
        self._db: dict[int, EventResponse] = {}
        self._id_counter = 1

    def list_all(self) -> list[EventResponse]:
        return list(self._db.values())

    # Atualizar para utilizar kwargs
    # def list_partial(self, *, skip: int = 0, limit: int = 20, city: str | None = None):
    def list_partial(self, *, skip: int = 0, limit: int = 20, **filters) -> list[EventResponse]:
        """
        Devolve um recorte paginado da coleção em memória, aplicando
        dinamicamente filtros recebidos como keyword-args.

        Exemplos de chamada:
            repo.list_partial(skip=0, limit=10)                    # sem filtros
            repo.list_partial(skip=0, limit=10, city="Recife")     # filtra por cidade
            repo.list_partial(skip=0, limit=10, xyz="ABC")         # filtra por outro campo
        """
        data: list[EventResponse] = list(self._db.values())
        
        # aplica cada filtro recebido
        for field, expected in filters.items():
            if expected is None:        # ignora filtros vazios
                continue

            def _match(event: EventResponse) -> bool:
                actual = getattr(event, field, None)
                # comparação "case-insensitive" para strings
                if isinstance(actual, str) and isinstance(expected, str):
                    return actual.lower() == expected.lower()
                return actual == expected

            data = [e for e in data if _match(e)]

        # paginação final
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
    
    # -----------------------------------------------------------------
    def clear(self) -> None:
        """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
        self._db.clear()
        self._id_counter = 1
    # -----------------------------------------------------------------

    def delete_all(self) -> None:
        """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
        self._db.clear()
        self._id_counter = 1

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
