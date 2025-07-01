# app/utils/cache.py
import json
import functools
import inspect
from typing import TypeVar

from collections.abc import Callable, Awaitable
from redis.asyncio import Redis
from fastapi import Depends
from structlog import get_logger

from app.deps import provide_redis

logger = get_logger().bind(module="cache")

T = TypeVar("T")

def _make_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """Gera uma chave determinística e curta."""
    return prefix + ":" + str(hash((args, tuple(sorted(kwargs.items())))))

def cached_json(prefix: str, ttl: int = 60):
    """Cachea o resultado JSON-serializável de um *endpoint* ou service async."""
    """Decorator para cachear o retorno JSON-serializável de uma função async."""
    def decorator(func: Callable[..., Awaitable[T]]):
        sig = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(
            *args,
            redis: Redis = Depends(provide_redis),   # ⬅ FastAPI resolve em runtime
            **kwargs,
        ):
            # 🔑  pega (ou reaproveita) a conexão Redis
            redis_client: Redis = await provide_redis()
            
            # # Se ainda for objeto Depends, quer dizer que estamos fora do FastAPI
            # if isinstance(redis, Depends):           # ← 👈 novo
            #     return await func(*args, **kwargs)
            
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            key = _make_key(prefix, bound.args, bound.kwargs)

            try:
                if (cached := await redis_client.get(key)):
                    logger.info("Cache hit", prefix=prefix, key=key)
                    return json.loads(cached)

                logger.debug("Cache miss", prefix=prefix, key=key)
                result: T = await func(*args, **kwargs)
                await redis_client.setex(key, ttl, json.dumps(result, default=str))
                logger.debug("Valor armazenado no cache", prefix=prefix, key=key, ttl=ttl)
                return result
            
            # 🔽 2) Qualquer problema ⇒ segue sem cache ----------------
            except Exception as e:
                logger.warning("Erro ao acessar o cache Redis", prefix=prefix, key=key, error=str(e))
                return await func(*args, **kwargs)
            
        return wrapper
    return decorator