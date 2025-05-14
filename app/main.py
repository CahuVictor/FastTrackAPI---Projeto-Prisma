from fastapi import FastAPI
# from app.api.v1.api_router import router as api_router
from app.api.v1.endpoints import eventos

# app = FastAPI(title="FastTrackAPI - Projeto Prisma")
# app.include_router(api_router)

app = FastAPI(
    title="FastTrackAPI – Projeto Prisma",
    description="API para gerenciamento de eventos, com integração de dados externos e validações via Pydantic.",
    version="1.0.0",
    contact={
        "name": "Mentoria Backend",
        "email": "mentor@example.com"
    }
)

app.include_router(eventos.router, prefix="/api/v1")