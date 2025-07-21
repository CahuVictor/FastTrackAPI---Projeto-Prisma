# app/repositories/event_mem.py
from structlog import get_logger

from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.event_update import ForecastInfoUpdate

from app.repositories.event import AbstractEventRepo

logger = get_logger().bind(module="event_mem")

class InMemoryEventRepo(AbstractEventRepo):
    def __init__(self):
        self._db: dict[int, EventResponse] = {}
        self._id_counter = 1

    def list_all(self) -> list[EventResponse]:
        logger.info("Listando todos os eventos", total=len(self._db))
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
        result = data[skip : skip + limit]
        
        logger.info("Listagem parcial de eventos", filtros=filters, total=len(result))
        return result

    def get(self, event_id: int) -> EventResponse | None:
        event = self._db.get(event_id)
        if event:
            logger.info("Evento recuperado", event_id=event_id)
        else:
            logger.warning("Evento não encontrado", event_id=event_id)
        return event
    
    def add(self, event: EventCreate, forecast_info: ForecastInfoUpdate | None = None) -> EventResponse:
        event_resp = EventResponse(
            id=self._id_counter,
            title=event.title,
            description=event.description,
            event_date=event.event_date,
            city=event.city,
            participants=event.participants,
            local_info=event.local_info,
            forecast_info=forecast_info,
        )
        self._db[self._id_counter] = event_resp
        logger.info("Evento adicionado", event_id=self._id_counter, title=event.title, city=event.city, date=event.event_date)
        self._id_counter += 1
        return event_resp

    def replace_all(self, events: list[EventResponse]) -> list[EventResponse]:
        self._db = {e.id: e for e in events}
        logger.info("Todos os eventos foram substituídos", total=len(events))
        return list(self._db.values())

    def replace_by_id(self, event_id: int, event: EventResponse) -> EventResponse:
        self._db[event_id] = event
        logger.info("Evento substituído", event_id=event_id)
        return event
    
    # -----------------------------------------------------------------
    def clear(self) -> None:
        """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
        self._db.clear()
        self._id_counter = 1
        logger.info("Repositório de eventos limpo")
    # -----------------------------------------------------------------

    def delete_all(self) -> None:
        """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
        self._db.clear()
        self._id_counter = 1
        logger.info("Todos os eventos foram deletados")

    def delete_by_id(self, event_id: int) -> bool:
        result = self._db.pop(event_id, None)
        if result:
            logger.info("Evento deletado", event_id=event_id)
            return True
        logger.warning("Tentativa de deletar evento inexistente", event_id=event_id)
        return False

    def update(self, event_id: int, data: dict) -> EventResponse:
        existing = self._db.get(event_id)
        if not existing:
            logger.error("Erro ao atualizar: evento não encontrado", event_id=event_id)
            raise ValueError("Evento não encontrado")
        for key, value in data.items():
            setattr(existing, key, value)
        self._db[event_id] = existing
        logger.info("Evento atualizado", event_id=event_id, campos=list(data.keys()))
        return existing
