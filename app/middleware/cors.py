# app\middleware\cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import get_settings

def init_cors(app: FastAPI) -> None:
    # settings = get_settings()

    # Aqui você pode ler da variável de ambiente depois se quiser:
    # allowed_origins = settings.allowed_origins or ["*"]
    allowed_origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://seusite.com.br",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
