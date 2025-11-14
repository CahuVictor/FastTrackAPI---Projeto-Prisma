# app/utils/cache.py
import json
import functools
import inspect
from typing import TypeVar

from collections.abc import Callable, Awaitable
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
from structlog import get_logger

from app.core.deps import provide_redis

logger = get_logger().bind(module="cache")

T = TypeVar("T")

def _make_key(prefix: str, bound_args: dict) -> str:
    """Gera uma chave determinística e curta."""
    """Evita tipos não determinísticos na key."""
    SAFE_TYPES = (str, int, float, bool, type(None))
    clean = {k: v for k, v in bound_args.items() if isinstance(v, SAFE_TYPES)}
    return prefix + ":" + str(hash(tuple(sorted(clean.items()))))

def cached_json(prefix: str, ttl: int = 60):
    """Cachea o resultado JSON-serializável de um *endpoint* ou service async."""
    """Decorator para cachear o retorno JSON-serializável de uma função async."""
    def decorator(func: Callable[..., Awaitable[T]]):
        sig = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs, ):
            # 🔑  pega (ou reaproveita) a conexão Redis
            redis_client: Redis = await provide_redis()
            
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            key = _make_key(prefix, bound.arguments)

            try:
                if (cached := await redis_client.get(key)):
                    logger.info("Cache hit", prefix=prefix, key=key)
                    return json.loads(cached)

                logger.debug("Cache miss", prefix=prefix, key=key)
                result: T = await func(*args, **kwargs)
                
                # await redis_client.setex(key, ttl, json.dumps(result, default=str))
                serializable = jsonable_encoder(result)
                await redis_client.setex(key, ttl, json.dumps(serializable))
                logger.debug("Valor armazenado no cache", prefix=prefix, key=key, ttl=ttl)
                # return result
                return serializable
            
            # 🔽 2) Qualquer problema ⇒ segue sem cache ----------------
            except Exception as e:
                logger.warning("Erro ao acessar o cache Redis", prefix=prefix, key=key, error=str(e))
                return await func(*args, **kwargs)
            
        return wrapper
    return decorator