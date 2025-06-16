# app/middleware/logging_middleware.py
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog import get_logger

from app.core.contextvars import request_user

logger = get_logger().bind(module="logging_middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            process_time = round(time.time() - start_time, 4)
            status_code = response.status_code if response else 500
            
            path = request.url.path

            # 🔕 Ignora rotas internas
            # ❌ não loga se for rota interna (mas ainda responde corretamente)
            if path.startswith("/docs") or path.startswith("/openapi") or path.startswith("/redoc"):
                return response

            # 📥 Informações adicionais
            user_agent = request.headers.get("user-agent", "unknown")
            user = request_user.get() or "anonymous"
            client = request.client.host if request.client else "unknown"

            logger.info(
                "HTTP request log",
                method=request.method,
                path=path,
                status_code=status_code,
                duration=process_time,
                client=client,
                user_agent=user_agent,
                user=user
            )
