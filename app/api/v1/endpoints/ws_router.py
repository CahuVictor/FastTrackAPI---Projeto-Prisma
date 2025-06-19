# api/v1/endpoints/ws_router.py
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Query
from app.websockets.ws_manager import manager
from app.websockets.ws_dashboard import notify_user_count

ws_router = APIRouter()

@ws_router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket, admin: bool = Query(False)):
    await manager.connect(websocket, is_admin=admin)
    await notify_user_count()
    try:
        while True:
            await websocket.receive_text()  # pode ser controle no futuro
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await notify_user_count()
