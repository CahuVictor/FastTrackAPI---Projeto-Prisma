# app/core/exception_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from structlog import get_logger

logger = get_logger().bind(module="exception_handlers")

async def db_connection_exception_handler(request: Request, exc: OperationalError):
    logger.error(
        "Database unavailable (caught globally)",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable: could not connect to the database. Please try again later."}
    )

# Pode ser criado outros handlers customizados aqui, ex:
# async def custom_not_found_handler(request: Request, exc: HTTPException):
#     ...
