# app/utils/cache.py
import json
import functools
import inspect
from typing import Callable, Awaitable, TypeVar
from redis.asyncio import Redis
from fastapi import Depends

from app.deps import provide_redis

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
            redis: Redis = await provide_redis()
            
            # # Se ainda for objeto Depends, quer dizer que estamos fora do FastAPI
            # if isinstance(redis, Depends):           # ← 👈 novo
            #     return await func(*args, **kwargs)
            
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            key = _make_key(prefix, bound.args, bound.kwargs)

            if (cached := await redis.get(key)):
                return json.loads(cached)

            result: T = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator