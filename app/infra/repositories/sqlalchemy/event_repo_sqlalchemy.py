# app/infra/repositories/sqlalchemy/event_repo_sqlalchemy.py
from __future__ import annotations

from sqlalchemy.orm import Session
from structlog import get_logger

from app.infra.db.tables.event_table import EventTable
from app.models.event import Event

logger = get_logger().bind(module="event_repo_sqlalchemy")

class EventRepoSQLAlchemy:
    """
    Implementação de EventRepository usando SQLAlchemy e EventTable como modelo ORM.

    Responsável por:
    - Mapear entre Event (domínio) e EventTable (infra/ORM).
    - Realizar operações CRUD no banco relacional.
    """
    
    def __init__(self, session: Session):
        """
        Inicializa o repositório com uma instância de sessão do SQLAlchemy (Session).
        """
        self.session = session
        logger.debug("EventRepoSQLAlchemy inicializado")

    # helpers de mapeamento
    def _to_domain(self, row: EventTable) -> Event:
        """
        Converte uma instância de EventTable (ORM) em uma entidade de domínio Event.

        Esta função faz o mapeamento campo-a-campo entre o modelo de infraestrutura
        (SQLAlchemy) e o modelo de domínio, garantindo que a camada de domínio
        permaneça desacoplada de detalhes de persistência.
        """
        return Event(
            id=row.id,
            title=row.title,
            description=row.description,
            event_date=row.event_date,
            city=row.city,
            participants=row.participants or [],
            views=row.views or 0,
            local_id=row.local_id,
            forecast_id=row.forecast_id,
        )
    
    def _update_row_from_domain(self, row: EventTable, event: Event) -> EventTable:
        """
        Atualiza uma instância de EventTable (ORM) com os dados vindos de uma
        entidade de domínio Event.

        Usado em operações de update para refletir as mudanças feitas no objeto
        de domínio na entidade mapeada pelo SQLAlchemy.
        """
        row.title = event.title
        row.description = event.description
        row.event_date = event.event_date
        row.city = event.city
        row.participants = event.participants
        row.views = event.views
        row.local_id = event.local_id
        row.forecast_id = event.forecast_id
        return row
    
    # contrato
    def add(self, event: Event) -> Event:
        """
        Persiste um novo Event no banco usando EventTable.

        Passos:
        - `add`: marca o objeto para INSERT.
        - `flush`: envia INSERT ao banco (gera ID se for PK autoincrement).
        """
        row = EventTable(
            title=event.title,
            description=event.description,
            event_date=event.event_date,
            city=event.city,
            participants=event.participants,
            views=event.views,
            local_info_id=event.local_id,
            forecast_info_id=event.forecast_id,
        )
        
        self.session.add(row)
        self.session.flush()  # garante id
        
        logger.info(
            "Evento adicionado no banco",
            event_id=row.id,
            title=row.title,
            city=row.city,
        )
        
        return self._to_domain(row)
    
    def get(self, event_id: int) -> Event | None:
        """
        Retorna um evento pelo seu ID ou `None` se não existir.
        """
        row = self.session.get(EventTable, event_id)
        
        if row:
            logger.info(
                "Evento encontrado no banco",
                event_id=row.id,
                title=row.title,
                city=row.city,
            )
            return self._to_domain(row)

        logger.info("Evento não encontrado no banco", event_id=event_id)
        return None

    def list(self, *, skip: int = 0, limit: int = 50, city: str | None = None) -> list[Event]:
        """
        Retorna uma sequência iterável de entidades de domínio Event, ordenadas
        por `event_date` (desc), com paginação e filtro opcional por cidade.

        Parâmetros:
        - skip: quantidade de registros a pular (offset).
        - limit: máximo de registros a retornar; se <= 0, não aplica limite.
        - city: se informado, filtra apenas eventos cuja cidade seja exatamente `city`.
        """
        query = self.session.query(EventTable)

        if city:
            query = query.filter(EventTable.city == city)
        
        query = query.order_by(EventTable.event_date.desc()).offset(skip)

        if limit > 0:
            query = query.limit(limit)
        
        rows = query.all()
        events = [self._to_domain(row) for row in rows]
        
        logger.info(
            "Listando eventos",
            total=len(events),
            skip=skip,
            limit=limit,
            city=city,
        )

        return events

    def update(self, event: Event) -> Event:
        """
        Atualiza campos específicos de um evento já existente.

        Levanta:
        - ValueError se o Event não possuir id.
        - KeyError se nenhum registro for encontrado com o id informado.
        """
        if event.id is None:
            logger.error("Tentativa de update sem id", event=event)
            raise ValueError("Cannot update Event without id")

        row = self.session.get(EventTable, event.id)
        if not row:
            logger.warning("Evento não encontrado para update", event_id=event.id)
            raise KeyError("Event not found")

        self._update_row_from_domain(row, event)
        self.session.flush()
        
        logger.info("Evento atualizado no banco", event_id=row.id, title=row.title)
        
        return self._to_domain(row)
    
    def delete(self, event_id: int) -> None:
        """
        Remove um evento específico pelo ID.
        """
        row = self.session.get(EventTable, event_id)
        if row:
            self.session.delete(row)
            self.session.flush()
            logger.info("Evento removido do banco", event_id=event_id)
        else:
            logger.info("Tentativa de remover evento inexistente", event_id=event_id)

#     def replace_by_id(self, event_id: int, event: EventResponse) -> EventResponse:
#         """
#         Substitui completamente os dados de um evento existente por novos valores, 
#         aproveitando local_info/forecast_info se existentes.
#         """
#         db_event = self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).first()
#         if not db_event:
#             logger.warning("Evento não encontrado", event_id=event_id)
#             raise ValueError("Evento não encontrado")
        
#         data = event.model_dump(exclude={"id"}, exclude_unset=True)
#         logger.debug("Dados recebidos para substituição", dados=data)
        
#         for key, value in data.items():
#             if key == "local_info" and value is not None:
#                 logger.debug("Atualizando local_info", event_id=event_id)
#                 db_event.local_info = ModelsLocalInfo(**value)
#             # elif key == "forecast_info":
#             #     try:
#             #         service: AbstractForecastService = Depends(provide_forecast_service)
#             #         # service: AbstractForecastService = _provide_forecast_service()
#             #         forecast = service.get_by_city_and_datetime(event.city, event.event_date)
#             #         db_event.forecast_info = ForecastInfo(**forecast.model_dump())
#             #         logger.debug("Forecast atualizado com sucesso", event_id=event_id)
#             #     except Exception as e:
#             #         logger.warning("Falha ao atualizar forecast, usando existente", error=str(e), event_id=event_id)
#             #         if value is not None:
#             #             db_event.forecast_info = ForecastInfo(**value)
#             # else:
#             elif key in {"title", "description", "event_date", "city", "participants", "views"}:
#                 setattr(db_event, key, value)
        
#         self.db.commit()
#         self.db.refresh(db_event)
#         return EventResponse.model_validate(db_event, from_attributes=True)

#     def replace_all(self, events):
#         """
#         Remove todos os eventos existentes e insere os novos.
#         """
#         self.db.query(ModelsEvent).delete()
#         simplified = [
#             ModelsEvent(
#                 title=e.title,
#                 description=e.description,
#                 event_date=e.event_date,
#                 city=e.city,
#                 participants=e.participants
#             )
#             for e in events
#         ]
#         self.db.bulk_save_objects(simplified)
#         self.db.commit()
#         logger.info("Todos os eventos foram substituídos")

#     def delete_by_id(self, event_id: int):
#         """
#         Remove um evento específico pelo ID.
#         """
#         self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).delete()
#         self.db.commit()
#         logger.info("Evento removido", event_id=event_id)
    
#     def delete_all(self) -> None:
#         """
#         Remove todos os eventos da base de dados.
#         """
#         self.db.query(ModelsEvent).delete()
#         self.db.commit()
#         logger.info("Todos os eventos foram apagados")

#     def update(self, event_id: int, data: dict):
#         """
#         Atualiza campos específicos de um evento via dicionário (`data`).
#         """
#         data = _clean_update_data(data)
#         self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).update(data)
#         self.db.commit()
#         return self.get(event_id)

# # def orm_to_response(event: Event) -> EventResponse:
# #     """
# #     Converte um objeto ORM Event em um objeto Pydantic EventResponse.
# #     Trata os relacionamentos para garantir compatibilidade.
# #     """
# #     return EventResponse(
# #         id=event.id,
# #         title=event.title,
# #         description=event.description,
# #         event_date=event.event_date,
# #         city=event.city,
# #         participants=event.participants,
# #         local_info=LocalInfo.model_validate(event.local_info) if event.local_info else None,
# #         forecast_info=ForecastInfoUpdate.model_validate(event.forecast_info) if event.forecast_info else None,
# #         views=event.views
# #         # created_at=event.created_at
# #     )

# def _clean_update_data(data: dict) -> dict:
#     # ⚠️ Remover campos que não podem ser atualizados diretamente
#     return {
#         k: v for k, v in data.items()
#         if k not in {"id", "local_info_id", "forecast_info_id"}
#     }
#     # Segurança: impede atualização de campos protegidos
#     # for field in ["id", "local_info_id", "forecast_info_id"]:
#     #     data.pop(field, None)