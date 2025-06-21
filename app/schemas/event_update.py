from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated # , Optional
from app.schemas.venue_type import VenueTypes
from datetime import datetime

class EventUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=100, description="Novo título do evento.", json_schema_extra={"example": "Encontro de Startups"})] = None
    description: Annotated[str | None, Field(description="Nova descrição do evento.", json_schema_extra={"example": "Evento com networking, pitch e painéis sobre inovação."})] = None
    event_date: Annotated[datetime | None, Field(description="Nova data e hora do evento.", json_schema_extra={"example": "2025-07-05T14:30:00"})] = None
    city: Annotated[str | None, Field(description="Nova cidade do evento.", json_schema_extra={"example": "Olinda"})] = None
    participants: Annotated[list[str] | None, Field(description="Nova lista de participantes.", json_schema_extra={"example": ["Alice", "Bruno", "Carla"]})] = None
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")

# class EventUpdate(BaseModel):
#     local_info: Annotated[dict|None, Field(description="Dados do local vindos da API externa", json_schema_extra={"example": {"capacity": 100}}, default=None)]
#     forecast_info: Annotated[dict|None, Field(description="Previsão do tempo da API pública", json_schema_extra={"example": {"temperature": 27.5}}, default=None)]
    
# Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead.
# (Extra keys: 'example'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide 
# at https://errors.pydantic.dev/2.11/migration/

class LocalInfoUpdate(BaseModel):
    location_name: Annotated[str | None, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"Empresa XYZ"})] = None
    capacity: Annotated[int | None, Field(ge=0, json_schema_extra={"example":100}, description="Capacidade máxima de pessoas")] = None
    venue_type: Annotated[VenueTypes | None, Field(description="Tipo de local (auditório, salão, etc.)")] = None
    is_accessible: Annotated[bool | None, Field(description="Possui acessibilidade", json_schema_extra={"example":False})] = None
    address: Annotated[str | None, Field(min_length=5, json_schema_extra={"example":"Rua Atualizada, 123"}, description="Endereço completo")] = None
    # past_events: Annotated[list[str] | None, Field(description="Histórico de eventos realizados", json_schema_extra={"example":["Evento A", "Evento B"]})] = None
    manually_edited: Annotated[bool, Field(description="Indica se os dados foram alterados manualmente", default=False, json_schema_extra={"example":False})]
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")

class ForecastInfoUpdate(BaseModel):
    forecast_datetime: Annotated[datetime | None, Field(description="Data e hora da previsão")] = None
    temperature: Annotated[float | None, Field(description="Temperatura prevista (°C)", json_schema_extra={"example":27.5})] = None
    weather_main: Annotated[str | None, Field(description="Condição geral (ex: Clear, Rain)", json_schema_extra={"example":"Clear"})] = None
    weather_desc: Annotated[str | None, Field(description="Descrição detalhada do clima", json_schema_extra={"example":"Céu limpo com poucas nuvens"})] = None
    humidity: Annotated[int | None, Field(description="Umidade relativa (%)")] = None
    wind_speed: Annotated[float | None, Field(description="Velocidade do vento (m/s)")] = None
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")