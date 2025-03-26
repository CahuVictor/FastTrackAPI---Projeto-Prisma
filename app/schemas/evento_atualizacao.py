from pydantic import BaseModel, Field
from typing import Annotated

class EventoAtualizacao(BaseModel):
    local_info: Annotated[dict, Field(description="Dados do local vindos da API externa")]
    forecast_info: Annotated[dict, Field(description="Previsão do tempo da API pública")]