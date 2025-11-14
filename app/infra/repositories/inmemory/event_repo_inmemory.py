# app/infra/repositories/inmemory/event_repo_inmemory.py
from __future__ import annotations

from structlog import get_logger
from typing import Dict, List
from datetime import datetime

from app.models.event import Event

logger = get_logger().bind(module="event_repo_inmemory")

class EventRepoInMemory:
    """
    Implementação de EventRepository inteiramente em memória.

    Mantém os mesmos comportamentos essenciais da versão SQLAlchemy:
    - `id` gerado automaticamente
    - `created_at` definido ao inserir
    - `updated_at` atualizado ao modificar
    
    Útil para:
    - Testes unitários.
    - Ambiente de desenvolvimento sem depender de banco.
    - Protótipos rápidos.
    """
    def __init__(self):
        # "banco" em memória: id -> Event
        self._storage: Dict[int, Event] = {}
        self._next_id: int = 1

        logger.debug("EventRepoInMemory inicializado")
    
    def _generate_id(self) -> int:
        new_id = self._next_id
        self._next_id += 1
        return new_id
    
    # ----------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------
    def add(self, event: Event) -> Event:
        """
        Adiciona um novo Event ao armazenamento em memória.
        Preenche automaticamente id, created_at e updated_at.
        """
        if event.id is None:
            event.id = self._generate_id()
        
        now = datetime.utcnow()
        event.created_at = now
        event.updated_at = now
        
        self._storage[event.id] = event
        
        logger.info(
            "Evento adicionado em memória",
            event_id=event.id,
            title=event.title,
            city=event.city,
            date=event.event_date,
        )

        return event
    
    # ----------------------------------------------------------------------
    # READ
    # ----------------------------------------------------------------------
    def get(self, event_id: int) -> Event | None:
        """
        Retorna um Event pelo id ou None se não existir.
        """
        event = self._storage.get(event_id)
        
        if event:
            logger.info(
                "Evento encontrado em memória",
                event_id=event_id,
                title=event.title,
                city=event.city,
                date=event.event_date,
            )
        else:
            logger.info("Evento não encontrado em memória", event_id=event_id)

        return event

    # ----------------------------------------------------------------------
    # LIST
    # ----------------------------------------------------------------------
    def list(self, *, skip: int = 0, limit: int = 20, city: str | None = None, **filters) -> list[Event]:
        """
        Devolve um recorte paginado da coleção em memória, aplicando
        dinamicamente filtros recebidos.

        Exemplos de chamada:
            repo.list_partial(skip=0, limit=10)                    # sem filtros
            repo.list_partial(skip=0, limit=10, city="Recife")     # filtra por cidade
            repo.list_partial(skip=0, limit=10, xyz="ABC")         # filtra por outro campo
        """
        events = list(self._storage.values())
        
        if city:
            events = [e for e in events if e.city == city]

        events.sort(key=lambda e: e.event_date, reverse=True)

        if skip:
            events = events[skip:]

        if limit > 0:
            events = events[:limit]

        logger.info(
            "Listando eventos em memória",
            total=len(events),
            skip=skip,
            limit=limit,
            city=city,
        )

        return events
    
    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update(self, event: Event) -> Event:
        """
        Atualiza um Event já existente em memória.
        Atualiza automaticamente updated_at.
        """
        if event.id is None:
            logger.error("Tentativa de update em memória sem id", event=event)
            raise ValueError("Cannot update Event without id")

        if event.id not in self._storage:
            logger.warning("Evento não encontrado em memória para update", event_id=event.id)
            raise KeyError("Event not found")
        
        # atualiza updated_at
        event.updated_at = datetime.utcnow()

        self._storage[event.id] = event

        logger.info(
            "Evento atualizado em memória",
            event_id=event.id,
            title=event.title,
            city=event.city,
            date=event.event_date,
            updated=event.updated_at,
        )

        return event

    # def replace_all(self, events: list[EventResponse]) -> list[EventResponse]:
    #     self._db = {e.id: e for e in events}
    #     logger.info("Todos os eventos foram substituídos", total=len(events))
    #     return list(self._db.values())

    # def replace_by_id(self, event_id: int, event: EventResponse) -> EventResponse:
    #     self._db[event_id] = event
    #     logger.info("Evento substituído", event_id=event_id)
    #     return event
    
    # # -----------------------------------------------------------------
    # def clear(self) -> None:
    #     """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
    #     self._db.clear()
    #     self._id_counter = 1
    #     logger.info("Repositório de eventos limpo")
    # # -----------------------------------------------------------------

    # def delete_all(self) -> None:
    #     """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
    #     self._db.clear()
    #     self._id_counter = 1
    #     logger.info("Todos os eventos foram deletados")

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def delete(self, event_id: int) -> bool:
        """
        Remove um Event do armazenamento em memória, se existir.
        """
        if event_id in self._storage:
            del self._storage[event_id]
            logger.info("Evento removido em memória", event_id=event_id)
        else:
            logger.info(
                "Tentativa de remover evento inexistente em memória",
                event_id=event_id,
            )