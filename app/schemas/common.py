# app\schemas\common.py
from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    """
    Modelo de resposta genérica para mensagens simples,
    como confirmações de sucesso ou avisos de tarefa agendada.
    """
    detail: str = Field(..., description="Tarefa de atualização de forecast agendada")
