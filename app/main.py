from fastapi import FastAPI

from app.api.v1.endpoints import eventos, auth          #  ←  agora importamos auth
# from app.services.auth_service import get_current_user          #  ←  dependência global


app = FastAPI(
    title="FastTrackAPI – Projeto Prisma",
    description="API para gerenciamento de eventos, com integração de dados externos e validações via Pydantic.",
    version="1.0.0",
    contact={
        "name": "Mentoria Backend",
        "email": "mentor@example.com"
    }
)

app.include_router(auth.router, prefix="/api/v1")

# app.include_router(
#     eventos.router,
#     prefix="/api/v1",
#     dependencies=[Depends(get_current_user)],   #  ←  proteção em bloco
# )

app.include_router(eventos.router, prefix="/api/v1")