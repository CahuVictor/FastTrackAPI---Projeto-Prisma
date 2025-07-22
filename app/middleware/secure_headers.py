# app/middleware/secure_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# from secure import SecureHeaders

# secure_headers = SecureHeaders()

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # response = await call_next(request)
        response: Response = await call_next(request)

        # Adiciona cabeçalhos de segurança à resposta
        # secure_headers.fastapi(response)
        
        # Headers de segurança recomendados
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
