# app/middleware/rate_limiter.py
from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware

from app.core.rate_limit_config import limiter

# Middleware para habilitar controle de taxa (rate limiting)
def setup_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
