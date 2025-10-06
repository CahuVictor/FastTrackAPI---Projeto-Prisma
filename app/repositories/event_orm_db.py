# app/repositories/event_orm_db.py
from sqlalchemy.orm import Session
from structlog import get_logger

from app.schemas.event_create import EventCreate, EventResponse
# from app.schemas.weather_forecast import ForecastInfo

# from app.schemas.event_update import ForecastInfoUpdate      # TODO

from app.repositories.event import AbstractEventRepo

from app.models.models_event import ModelsEvent
from app.models.models_local_info import ModelsLocalInfo
# from app.models.models_forecast_info import ModelsForecastInfo

logger = get_logger().bind(module="repo_eventos")

class SQLEventRepo(AbstractEventRepo):
    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma instância de sessão do SQLAlchemy (Session).
        """
        self.db = db

    def list_all(self):
        """
        Retorna todos os eventos da base de dados.
        Retorna já convertidos para o schema EventResponse.
        """
        db_events = self.db.query(ModelsEvent).all()
        
        return [
            EventResponse.model_validate(e, from_attributes=True)
            for e in db_events
        ]

    def list_partial(self, skip: int = 0, limit: int = 20, **filters):
        """
        Retorna uma lista paginada de eventos, com filtros dinâmicos aplicáveis
        (ex: `city="Recife"` ou `title="Festival"`).
        Retorna já convertidos para o schema EventResponse.
        """
        query = self.db.query(ModelsEvent)
        for attr, value in filters.items():
            if value is not None and hasattr(ModelsEvent, attr):
                query = query.filter(getattr(ModelsEvent, attr) == value)
        
        db_events = query.offset(skip).limit(limit).all()
        
        return [
            EventResponse.model_validate(e, from_attributes=True)
            for e in db_events
        ]

    def get(self, event_id: int):
        """
        Retorna um evento pelo seu ID ou `None` se não existir.
        """
        db_event = self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).first()
        if db_event is None:
            return None
        return EventResponse.model_validate(db_event, from_attributes=True)

    # def add(self, event: EventCreate, forecast_info: ForecastInfo | None = None):      # TODO
    def add(self, event: EventCreate):
        """
        Cria e salva um novo evento no banco de dados.
        Também salva `local_info` e `forecast_info` se presentes.
        """
        db_event = ModelsEvent(
            title=event.title,
            description=event.description,
            event_date=event.event_date,
            city=event.city,
            participants=event.participants or []
        )

        # Associa local_info (se estiver presente no EventCreate)
        if event.local_info:
            db_event.local_info = ModelsLocalInfo(**event.local_info.model_dump())

        # Associa forecast_info (mock ou real)
        # if forecast_info:      # TODO
            # db_event.forecast_info = ForecastInfo(**forecast_info.model_dump())      # TODO
        db_event.forecast_info = None

        # Persiste no banco
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)

        logger.info("Evento adicionado no banco", event_id=db_event.id, title=db_event.title)
        return EventResponse.model_validate(db_event, from_attributes=True)

    def replace_by_id(self, event_id: int, event: EventResponse) -> EventResponse:
        """
        Substitui completamente os dados de um evento existente por novos valores, 
        aproveitando local_info/forecast_info se existentes.
        """
        db_event = self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).first()
        if not db_event:
            logger.warning("Evento não encontrado", event_id=event_id)
            raise ValueError("Evento não encontrado")
        
        data = event.model_dump(exclude={"id"}, exclude_unset=True)
        logger.debug("Dados recebidos para substituição", dados=data)
        
        for key, value in data.items():
            if key == "local_info" and value is not None:
                logger.debug("Atualizando local_info", event_id=event_id)
                db_event.local_info = ModelsLocalInfo(**value)
            # elif key == "forecast_info":
            #     try:
            #         service: AbstractForecastService = Depends(provide_forecast_service)
            #         # service: AbstractForecastService = _provide_forecast_service()
            #         forecast = service.get_by_city_and_datetime(event.city, event.event_date)
            #         db_event.forecast_info = ForecastInfo(**forecast.model_dump())
            #         logger.debug("Forecast atualizado com sucesso", event_id=event_id)
            #     except Exception as e:
            #         logger.warning("Falha ao atualizar forecast, usando existente", error=str(e), event_id=event_id)
            #         if value is not None:
            #             db_event.forecast_info = ForecastInfo(**value)
            # else:
            elif key in {"title", "description", "event_date", "city", "participants", "views"}:
                setattr(db_event, key, value)
        
        self.db.commit()
        self.db.refresh(db_event)
        return EventResponse.model_validate(db_event, from_attributes=True)

    def replace_all(self, events):
        """
        Remove todos os eventos existentes e insere os novos.
        """
        self.db.query(ModelsEvent).delete()
        simplified = [
            ModelsEvent(
                title=e.title,
                description=e.description,
                event_date=e.event_date,
                city=e.city,
                participants=e.participants
            )
            for e in events
        ]
        self.db.bulk_save_objects(simplified)
        self.db.commit()
        logger.info("Todos os eventos foram substituídos")

    def delete_by_id(self, event_id: int):
        """
        Remove um evento específico pelo ID.
        """
        self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).delete()
        self.db.commit()
        logger.info("Evento removido", event_id=event_id)
    
    def delete_all(self) -> None:
        """
        Remove todos os eventos da base de dados.
        """
        self.db.query(ModelsEvent).delete()
        self.db.commit()
        logger.info("Todos os eventos foram apagados")

    def update(self, event_id: int, data: dict):
        """
        Atualiza campos específicos de um evento via dicionário (`data`).
        """
        data = _clean_update_data(data)
        self.db.query(ModelsEvent).filter(ModelsEvent.id == event_id).update(data)
        self.db.commit()
        return self.get(event_id)

# def orm_to_response(event: Event) -> EventResponse:
#     """
#     Converte um objeto ORM Event em um objeto Pydantic EventResponse.
#     Trata os relacionamentos para garantir compatibilidade.
#     """
#     return EventResponse(
#         id=event.id,
#         title=event.title,
#         description=event.description,
#         event_date=event.event_date,
#         city=event.city,
#         participants=event.participants,
#         local_info=LocalInfo.model_validate(event.local_info) if event.local_info else None,
#         forecast_info=ForecastInfoUpdate.model_validate(event.forecast_info) if event.forecast_info else None,
#         views=event.views
#         # created_at=event.created_at
#     )

def _clean_update_data(data: dict) -> dict:
    # ⚠️ Remover campos que não podem ser atualizados diretamente
    return {
        k: v for k, v in data.items()
        if k not in {"id", "local_info_id", "forecast_info_id"}
    }
    # Segurança: impede atualização de campos protegidos
    # for field in ["id", "local_info_id", "forecast_info_id"]:
    #     data.pop(field, None)