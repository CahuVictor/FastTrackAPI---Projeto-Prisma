# app/middleware/rate_limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Função para obter IP remoto do cliente
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500/minute"]
)

# Middleware para habilitar controle de taxa (rate limiting)
def setup_rate_limiter(app):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
