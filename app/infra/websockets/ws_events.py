# app/websockets/events.py
from app.infra.websockets.ws_manager import manager

# ───────────────────────── notificações upload ──────────────────────────

async def notify_upload_progress(title: str):
    """Envia progresso linha‑a‑linha durante upload em lote."""
    await manager.broadcast(f"✅ Evento '{title}' adicionado")

async def notify_upload_error(error: str):
    """Envia erros ocorridos durante o upload em lote."""
    await manager.broadcast(f"❌ Erro durante upload: {error}")

async def notify_upload_end(total: int):
    """Envia mensagem de finalização do upload em lote."""
    await manager.broadcast(f"🏁 Upload finalizado com {total} eventos")

# ───────────────────────── eventos individuais ──────────────────────────

async def notify_event_created(event_title: str):
    """Notifica administradores sobre a criação de um novo evento."""
    await manager.broadcast(f"📥 Novo evento: {event_title}", to_admins=True)

async def notify_event_viewed_update(event_id: int, views: int) -> None:
    """Atualiza em tempo‑real o número de visualizações de um evento."""
    await manager.broadcast(f"👁 Evento {event_id} agora com {views} visualizações")
 
# ───────────────────────── substituição em massa ────────────────────────

async def notify_replace_started():
    await manager.broadcast("🔁 Substituição de todos os eventos iniciada...", to_admins=True)

async def notify_replace_done():
    await manager.broadcast("✅ Substituição concluída", to_admins=True)

# ───────────────────────── ranking / dashboard ──────────────────────────

async def notify_top_viewed_update(titles: list[str]) -> None:
    """Envia a lista atual de eventos mais vistos (títulos) para todos."""
    joined = ", ".join(titles)
    await manager.broadcast(f"📈 Top eventos mais vistos: {joined}")

