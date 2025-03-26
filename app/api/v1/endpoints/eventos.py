from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/eventos", tags=["eventos"])
def listar_eventos():
    return {"mensagem": "Lista de eventos (exemplo inicial)"}