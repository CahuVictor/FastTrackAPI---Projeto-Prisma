# app/utils/patch.py
from fastapi import HTTPException
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta

from app.schemas.event_create import EventResponse
from app.schemas.event_update import EventUpdate, LocalInfoUpdate, ForecastInfoUpdate
from app.schemas.weather_forecast import ForecastInfoResponse

def should_update_forecast(forecast_info: ForecastInfoResponse | None) -> bool:
    if not forecast_info:
        return True
    if forecast_info.updated_at:
        return datetime.now(timezone.utc) - forecast_info.updated_at > timedelta(days=1)
    return False

# TODO criar função para localinfo update

def update_event_forecast(
    event: EventResponse, 
    update: ForecastInfoUpdate, 
):
    """
    Atualiza parcial e de forma segura os campos de forecast_info aninhados do evento.
    Se forecast_info estiver ausente (None), cria o objeto diretamente.
    """
    try:
        update_data = update.model_dump(exclude_unset=True)
        
        if event.forecast_info is None:            
            # Cria novo forecast_info com timestamp atual
            update_data.setdefault("updated_at", datetime.now(timezone.utc))
            
        else:
            # Merge com o existente
            base_data = event.forecast_info.model_dump()
            base_data.update(update_data)
            update_data = base_data

        # Converte para ForecastInfoResponse antes de atribuir
        event.forecast_info = ForecastInfoResponse(**update_data)
        
    except ValidationError as ve:
        # Você pode fazer log, print, raise HTTPException, etc
        # Exemplo: lançar erro HTTP para o FastAPI capturar e retornar pro usuário
        raise HTTPException(status_code=422, detail=ve.errors())

    return event

def update_event(
                 event: EventResponse, 
                 update: EventUpdate | LocalInfoUpdate | ForecastInfoUpdate, 
                 attr: str | None = None
):
    """
    Atualiza parcial e de forma segura o evento ou seus campos aninhados.
    - Se attr for None, atualiza diretamente os campos do evento.
    - Se attr for 'forecast_info' ou 'local_info', faz a atualização parcial segura do objeto aninhado.
    """
    
    try:
        if attr is None:
            # Atualiza os campos do evento principal
            update_data = update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(event, field, value)
        else:
            if attr == "forecast_info":
                from typing import cast
                # cast() para informar explicitamente ao MyPy que update é do tipo ForecastInfoUpdate
                return update_event_forecast(event, cast(ForecastInfoUpdate, update))
                # return update_event_forecast(event, update)
            else:
                # Atualiza um campo aninhado (ex: local_info, forecast_info)
                objeto = getattr(event, attr)
                dados_atualizados = objeto.model_dump() if objeto else {}
                update_data = update.model_dump(exclude_unset=True)
                dados_atualizados.update(update_data)
                # Descobre a classe do objeto aninhado
                field_cls = type(objeto) if objeto else None
                # Se não existir, pega o type pelo update (usando __annotations__ se quiser ser mais robusto)
                if field_cls is None and hasattr(event, '__annotations__'):
                    field_cls = event.__annotations__.get(attr)
                if field_cls:
                    setattr(event, attr, field_cls(**dados_atualizados))
                else:
                    # fallback (não deveria acontecer em uso normal)
                    setattr(event, attr, dados_atualizados)
    except ValidationError as ve:
        # Você pode fazer log, print, raise HTTPException, etc
        # Exemplo: lançar erro HTTP para o FastAPI capturar e retornar pro usuário
        raise HTTPException(status_code=422, detail=ve.errors())
    return event