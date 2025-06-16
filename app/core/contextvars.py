# app/core/contextvars.py
import contextvars

# Variável global de contexto por requisição
request_user: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_user", default=None
)
