# app/utils/patch.py
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.event_create import EventResponse
from app.schemas.event_update import EventUpdate, LocalInfoUpdate, ForecastInfoUpdate

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