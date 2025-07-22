# 🔐 Hardening de Segurança

Este documento detalha as práticas aplicadas para reforçar a segurança da aplicação FastAPI e aponta o que ainda está pendente.

---

## ✅ Implementado

### 🛡️ A. Validação e Sanitização de Entradas

- Utilização rigorosa do **Pydantic** para validação de dados.
- Uso de `constr`, `conint`, regex e validações customizadas.
- Exemplo presente nos schemas `UserInput`, `EventoCreate`, `EventoUpdate`.

---

### 🚫 B. Proteção contra CORS (❌ PENDENTE)

- 🔴 **CORS Middleware não implementado.**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seusite.com.br"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### ⏳ C. Rate Limiting com SlowAPI

- ✅ Implementado em `middleware/rate_limiter.py`
- ✅ Middleware ativado via `setup_rate_limiter(app)`
- ✅ Decoradores `@limiter.limit(...)` aplicados nas rotas:
  - `/auth/login` – 10/min
  - `/events/download` e `/events/upload` – 20/min
  - `/users`, `/users/{username}` – 10-20/min
  - `/events` – 60/min
- ✅ Testado com `test_rate_limiter.py`

---

### 🗝️ D. Segurança com JWT

- ✅ Implementado uso de JWT com:
  - Chave secreta forte (`SECRET_KEY`)
  - Expiração de token
  - Algoritmo `HS256`
  - Validação com `jwt.decode(...)`
- Proteção implementada nas dependências `get_current_user`.

---

### 🗄️ E. Banco de Dados Seguro

- ✅ ORM usado: `SQLAlchemy`
- ✅ Senhas com `passlib.hash.bcrypt`
- Sem SQL bruto exposto nas queries.

---

### 🔍 F. Headers HTTP Seguros

- ✅ Middleware implementado em `secure_headers.py` com `secure.SecureHeaders`.
- ✅ Testado em `test_secure_headers.py`.
- ✅ Middleware adicionado via `app.add_middleware(SecureHeadersMiddleware)`.

```python
# app/middleware/secure_headers.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"]
        return response
```

Esses headers ajudam a prevenir ataques como XSS, clickjacking, e mimetyping.

Para testar via CMD:
```bash
curl -I http://localhost:8000
```

Você deve receber headers como:

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

---

## 📊 Observabilidade

### 📈 Métricas com Prometheus

- ✅ `prometheus-fastapi-instrumentator` expõe `/metrics`
- ✅ Docker Compose com serviço do Prometheus
- ✅ Scraping configurado em `infra/prometheus.yml`

#### ⚠️ Dashboard Grafana

- ⚠️ **PENDENTE finalizar painel no Grafana**
- Painéis descritos e prontos para importação

---

### 📡 Tracing com OpenTelemetry + Jaeger

- ✅ `opentelemetry-instrumentation-fastapi` integrado
- ✅ `tracing_config.py` cria e expõe spans
- ✅ Docker Compose com `jaeger` rodando

#### ⚠️ Pendências

- ⚠️ `JaegerExporter` está depreciado → migrar para `OTLPSpanExporter`
- ⚠️ Adicionar spans manuais em pontos críticos (DB, parsing, IO)

---

## ✅ Middleware Global de Logging

- ✅ `logging_middleware.py` mede latência e loga path, status, user-agent, IP, etc.
- ✅ Ignora rotas internas como `/docs`, `/redoc`, `/openapi.json`

---

## ✅ Resumo

| Item                          | Status    |
|-------------------------------|-----------|
| Validação com Pydantic       | ✅ Feito  |
| Middleware CORS              | ❌ Pendente |
| Rate Limiting (SlowAPI)      | ✅ Feito  |
| JWT com expiração            | ✅ Feito  |
| Headers HTTP seguros         | ✅ Feito  |
| ORM e senha com hash         | ✅ Feito  |
| Logging middleware           | ✅ Feito  |
| Prometheus (métricas)        | ✅ Feito  |
| Grafana                      | ⚠️ Parcial |
| OpenTelemetry + Jaeger       | ✅ Feito  |
| Tracing com spans manuais    | ⚠️ Pendente |
| OTLP Exporter                | ⚠️ Pendente |

---

## 📌 Próximos Passos

- [ ] Adicionar `CORSMiddleware` com domínio confiável
- [ ] Finalizar painel no Grafana
- [ ] Migrar `JaegerExporter` para `OTLPSpanExporter`
- [ ] Adicionar spans personalizados

---

[⬅️ Voltar ao índice](../README.md)
