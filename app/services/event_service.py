# app/services/event_service.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from structlog import get_logger

from app.models.event import Event
from app.repositories.event_repo import EventRepository
from app.schemas.event_create import EventCreate
from app.schemas.event_update import EventUpdate
from app.utils.h_events import order_and_slice, ensure_aware

logger = get_logger().bind(module="event_service")


class EventService:
    """
    Application service responsável pelos casos de uso relacionados a eventos.

    Orquestra:
    - mapeamento entre schemas e domínio (Event)
    - regras de negócio
    - chamadas ao repositório (EventRepository)
    """

    def __init__(self, repo: EventRepository) -> None:
        """
        Args:
            repo: Implementação concreta de EventRepository
                  (SQLAlchemy, InMemory, etc.).
        """
        self.repo = repo

    # ------------------------------------------------------------------ #
    # CRUD básico
    # ------------------------------------------------------------------ #
    def list_events(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
    ) -> List[Event]:
        """
        Lista eventos com paginação e filtro opcional por cidade.

        Args:
            skip: Quantos registros pular (offset).
            limit: Quantos registros retornar no máximo.
            city: Se informado, filtra apenas eventos dessa cidade.

        Returns:
            Lista de entidades de domínio Event.
        """
        events = self.repo.list(skip=skip, limit=limit, city=city)
        logger.info(
            "Eventos listados com sucesso",
            total=len(events),
            skip=skip,
            limit=limit,
            city=city,
        )
        return events

    def list_all_events(self) -> List[Event]:
        """
        Lista todos os eventos sem paginação.

        Returns:
            Lista completa de entidades Event.
        """
        events = self.repo.list(skip=0, limit=0, city=None)
        logger.info("Todos os eventos listados", total=len(events))
        return events

    def get_event(self, event_id: int) -> Event | None:
        """
        Recupera um evento sem alterar o número de views.

        Args:
            event_id: Identificador do evento.

        Returns:
            Event se encontrado, ou None se não existir.
        """
        event = self.repo.get(event_id)
        if event:
            logger.info("Evento recuperado", event_id=event_id, title=event.title)
        else:
            logger.info("Evento não encontrado em get_event", event_id=event_id)
        return event

    def view_event(self, event_id: int) -> Event:
        """
        Recupera um evento e incrementa o contador de visualizações.

        Args:
            event_id: Identificador do evento.

        Returns:
            Entidade Event já persistida com o views incrementado.

        Raises:
            KeyError: Se o evento não for encontrado.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Tentativa de visualizar evento inexistente", event_id=event_id)
            raise KeyError("Event not found")

        event.views += 1
        logger.info("Incrementando views", event_id=event_id, views=event.views)
        updated = self.repo.update(event)
        return updated

    def create_event(self, payload: EventCreate) -> Event:
        """
        Cria um novo evento a partir do payload de entrada.

        Args:
            payload: Dados do evento validados via EventCreate.

        Returns:
            Entidade Event criada e persistida.
        """
        event = Event(
            title=payload.title,
            description=payload.description,
            event_date=payload.event_date,
            city=payload.city,
            participants=payload.participants,
            local_id=payload.local_id,
            forecast_id=payload.forecast_id,
            # created_at/updated_at ficam a cargo do repo
        )
        created = self.repo.add(event)
        logger.info("Evento criado com sucesso", event_id=created.id, title=created.title)
        return created

    def update_event(self, event_id: int, payload: EventUpdate) -> Event:
        """
        Aplica um patch parcial em um evento existente.

        Args:
            event_id: Identificador do evento a ser atualizado.
            payload: Campos opcionais com as alterações desejadas.

        Returns:
            Entidade Event atualizada e persistida.

        Raises:
            KeyError: Se o evento não for encontrado.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Tentativa de atualizar evento inexistente", event_id=event_id)
            raise KeyError("Event not found")

        if payload.title is not None:
            event.title = payload.title
        if payload.description is not None:
            event.description = payload.description
        if payload.event_date is not None:
            event.event_date = payload.event_date
        if payload.city is not None:
            event.city = payload.city
        if payload.participants is not None:
            event.participants = payload.participants
        if payload.local_id is not None:
            event.local_id = payload.local_id
        if payload.forecast_id is not None:
            event.forecast_id = payload.forecast_id

        updated = self.repo.update(event)
        logger.info("Evento atualizado com sucesso", event_id=updated.id)
        return updated

    def delete_event(self, event_id: int) -> None:
        """
        Remove um evento existente.

        Args:
            event_id: Identificador do evento a ser removido.

        Raises:
            KeyError: Se o evento não for encontrado.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Tentativa de deletar evento inexistente", event_id=event_id)
            raise KeyError("Event not found")

        self.repo.delete(event_id)
        logger.info("Evento deletado com sucesso", event_id=event_id)
    
    # ------------------------------------------------------------------ #
    # Casos de uso avançados (top soon, top viewed, download, batch, etc.)
    # ------------------------------------------------------------------ #
    def get_top_soon_events(self, limit: int) -> List[Event]:
        """
        Retorna os `limit` eventos com data mais próxima a partir de agora.

        Args:
            limit: Quantidade máxima de eventos a retornar.

        Returns:
            Lista de eventos futuros ordenados por data/hora (mais próximos primeiro).
        """
        # ✅ aware - retorna um datetime aware (com fuso horário)
        #     naive - não usar datetime naive (sem fuso horário), pois irá dificultar a ordenação depois na consulta
        now = datetime.now(timezone.utc)
        events = self.list_all_events()

        future_events = [
            ev for ev in events
            if ensure_aware(ev.event_date) >= now
        ]

        most_soon = order_and_slice(
            future_events,
            key_fn=lambda ev: ev.event_date,
            limit=limit,
        )

        logger.info(
            "Eventos mais próximos calculados",
            total=len(most_soon),
            limit=limit,
        )
        return most_soon

    def get_top_viewed_events(self, limit: int) -> List[Event]:
        """
        Retorna os `limit` eventos mais vistos.

        Critério de ordenação:
        - `views` desc (mais visualizados primeiro);
        - `event_date` asc em caso de empate.

        Args:
            limit: Quantidade máxima de eventos a retornar.

        Returns:
            Lista de eventos ordenados por popularidade.
        """
        events = self.list_all_events()

        most_viewed = order_and_slice(
            events,
            key_fn=lambda ev: (-ev.views, ev.event_date),
            limit=limit,
        )

        logger.info(
            "Eventos mais vistos calculados",
            total=len(most_viewed),
            limit=limit,
        )
        return most_viewed

    def create_events_batch(self, payloads: List[EventCreate]) -> List[Event]:
        """
        Cria múltiplos eventos em lote.

        Args:
            payloads: Lista de payloads EventCreate.

        Returns:
            Lista de entidades Event recém-criadas.
        """
        created_events: List[Event] = []
        for payload in payloads:
            created = self.create_event(payload)
            created_events.append(created)

        logger.info(
            "Eventos criados em lote",
            total=len(created_events),
        )
        return created_events

    def replace_all_events(self, new_events: List[Event]) -> List[Event]:
        """
        Substitui completamente a coleção de eventos.

        Implementação simples:
        - lista todos os eventos atuais;
        - deleta um por um;
        - insere os novos eventos.

        Args:
            new_events: Lista de entidades Event que passarão a representar
                        o estado completo do repositório.

        Returns:
            Lista de eventos que foram persistidos.
        """
        # remove todos
        existing = self.list_all_events()
        for ev in existing:
            self.repo.delete(ev.id)  # type: ignore[arg-type]

        # adiciona todos novamente
        persisted: List[Event] = []
        for ev in new_events:
            # ignoramos created_at/updated_at informados de fora:
            # o repo é responsável por setar esses campos.
            ev.id = None  # garante que serão recriados
            persisted.append(self.repo.add(ev))

        logger.info(
            "Todos os eventos foram substituídos",
            total=len(persisted),
        )
        return persisted

    def replace_event_by_id(self, event_id: int, new_event: Event) -> Event:
        """
        Substitui completamente os dados de um evento existente.

        Args:
            event_id: ID do evento a ser substituído.
            new_event: Entidade Event contendo o novo estado (exceto id).

        Returns:
            Entidade Event após a substituição/persistência.

        Raises:
            KeyError: Se o evento não for encontrado.
        """
        existing = self.repo.get(event_id)
        if not existing:
            logger.warning("Tentativa de substituir evento inexistente", event_id=event_id)
            raise KeyError("Event not found")

        # preserva o id, mas deixa created_at/updated_at a cargo do repo
        new_event.id = event_id
        replaced = self.repo.update(new_event)

        logger.info(
            "Evento substituído por completo",
            event_id=event_id,
            title=replaced.title,
        )
        return replaced
