# app/core/rate_limit_config.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# Cria o limiter com uma política padrão
limiter = Limiter(
    # Função para obter IP remoto do cliente
    key_func=get_remote_address,
    # Middleware para habilitar controle de taxa (rate limiting)
    default_limits=["500/minute"]
)
