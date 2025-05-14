from pydantic import BaseModel, Field
from typing import Annotated

class EventUpdate(BaseModel):
    local_info: Annotated[dict|None, Field(description="Dados do local vindos da API externa", json_schema_extra={"example": {"capacity": 100}}, default=None)]
    forecast_info: Annotated[dict|None, Field(description="Previsão do tempo da API pública", json_schema_extra={"example": {"temperature": 27.5}}, default=None)]
    
# Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead.
# (Extra keys: 'example'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide 
# at https://errors.pydantic.dev/2.11/migration/