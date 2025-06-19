# app/websockets/dashboard.py
from app.websockets.ws_manager import manager

# ───────────────────────── usuários online ──────────────────────────────

async def notify_user_count() -> None:
    """Atualiza o total de usuários conectados (qualquer perfil)."""
    count = len(manager.active_connections)
    await manager.broadcast(f"👥 Usuários online: {count}")

async def notify_admin_user_count() -> None:
    """Atualiza o total de administradores conectados."""
    count = len(manager.admin_connections)
    await manager.broadcast(f"👥 Admins online: {count}", to_admins=True)
