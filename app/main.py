# app\main.py
from fastapi import FastAPI
from structlog import get_logger
import os
import logging
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError
# from prometheus_fastapi_instrumentator import Instrumentator
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.controllers.api_router import router as api_router

# from app.services.auth_service import get_current_user          #  ←  dependência global

from app.core.logging_config import configure_logging
from app.core.exception_handlers import db_connection_exception_handler
from app.core.tracing_config import configure_tracing

from app.infra.middleware.logging_middleware import LoggingMiddleware
from app.infra.middleware.secure_headers import SecureHeadersMiddleware
from app.infra.middleware.rate_limiter import setup_rate_limiter
from app.infra.middleware.cors import init_cors

configure_logging()

logger = get_logger().bind(app="FastTrackAPI", env="dev")

uvicorn_log = logging.getLogger("uvicorn.error")   # <- o mesmo que imprime “INFO: …”

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 CÓDIGO DE STARTUP  (executa antes do app ficar pronto)
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "8000")
    if app.docs_url:
        # logger.info("Swagger UI (interativo)",
        #             url=f"http://{host}:{port}{app.docs_url}")
        uvicorn_log.info("Swagger UI (interativo): %s%s",
                         f"http://{host}:{port}", app.docs_url)
    if app.redoc_url:
        # logger.info("ReDoc (documentação formal)",
        #             url=f"http://{host}:{port}{app.redoc_url}")
        uvicorn_log.info("ReDoc (documentação): %s%s",
                         f"http://{host}:{port}", app.redoc_url)
    yield          # ← FastAPI levanta o app aqui
    
    # 🔸 CÓDIGO DE SHUTDOWN  (executa quando o servidor está parando)
    logger.info("Aplicação finalizada.")

app = FastAPI(
    title="FastTrackAPI – Projeto Prisma",
    description="API para gerenciamento de eventos, com integração de dados externos e validações via Pydantic.",
    lifespan=lifespan,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Mentoria Backend",
        "email": "mentor@example.com"
    }
)

init_cors(app)

app.include_router(api_router)

@app.get("/ping")
def ping():
    logger.info("pong", route="/ping")
    return {"msg": "pong"}

# Middleware de logging HTTP
app.add_middleware(LoggingMiddleware)

app.add_middleware(SecureHeadersMiddleware)

setup_rate_limiter(app)

# Registra o handler global
app.add_exception_handler(OperationalError, db_connection_exception_handler)

# instrumentator = Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# configure_tracing(agent_host="localhost")  # "jaeger" se dentro do Docker
# FastAPIInstrumentor.instrument_app(app)