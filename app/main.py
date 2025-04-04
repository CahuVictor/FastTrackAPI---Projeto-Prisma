from fastapi import FastAPI
from app.api.v1.api_router import router as api_router

app = FastAPI(title="FastTrackAPI - Projeto Prisma")
app.include_router(api_router)
