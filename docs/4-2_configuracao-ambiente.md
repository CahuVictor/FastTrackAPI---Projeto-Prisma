# 🔧 Configuração por Ambiente + Fallback Seguro

> Documento focado apenas na feature **Settings / .env**.  Para visão geral do projeto, consulte o README principal.

---

## 1 ▪ Por que separar ambientes?

| Ambiente          | Objetivo                             | O que muda                                                   |
| ----------------- | ------------------------------------ | ------------------------------------------------------------ |
| **dev**           | Trabalho diário, auto‑reload, debug. | BD/Redis locais, segredos fictícios.                         |
| **test**          | `pytest` + CI (Postgres).            | BD isolado, possivelmente Redis mockado/desligado.           |
| **test.inmemory** | Testes turbo em RAM.                 | `DB_URL=sqlite:///:memory:` → zero I/O de disco.             |
| **prod**          | Usuários reais.                      | Hostnames internos, segredos de Secret‑Manager, logs `INFO`. |

> **Dev ≠ Test** – a suíte de testes destrói dados sem atrapalhar seu BD local.

---

## 2 ▪ Arquivos `.env`

| Arquivo              | Quando é lido       | Exemplo mínimo                                           |
| -------------------- | ------------------- | -------------------------------------------------------- |
| `.env`               | default/dev         | `ENVIRONMENT=dev`  `DB_URL=postgres://localhost/dev_db`  |
| `.env.test`          | `ENV=test`          | `ENVIRONMENT=test` `DB_URL=postgres://localhost/test_db` |
| `.env.test.inmemory` | `ENV=test.inmemory` | `DB_URL=sqlite:///:memory:`                              |
| `.env.prod`          | `ENV=prod`          | `DB_URL=postgres://postgres/prod_db`                     |

Nunca commitamos segredos de produção; eles entram via variables do host ou secret‑manager.

---

## 3 ▪ Exemplo completo de `.env` (dev)

```ini
# ── Modo ─────────────────────────
ENVIRONMENT=dev
DEBUG=true
TESTING=false
RELOAD=true

# ── Build info (gerado se ausente) ─
# BUILD_TIMESTAMP e GIT_SHA podem ser omitidos localmente; o Settings gera.

# ── DB / Cache ───────────────────
DB_URL=postgresql://prisma:prisma123@localhost:5432/prisma_db
REDIS_URL=redis://localhost:6379/0

# ── Auth ─────────────────────────
AUTH_SECRET_KEY=dev-super-secret
ACCESS_TOKEN_EXPIRE_MIN=1440

# ── Logging ──────────────────────
LOG_LEVEL=DEBUG
LOG_FORMAT=plain

# ── Observabilidade ──────────────
SENTRY_DSN=

# ── CORS ─────────────────────────
ALLOWED_ORIGINS=http://localhost,https://127.0.0.1:3000

# ── Filas / tarefas ──────────────
CELERY_BROKER_URL=redis://redis:6379/1

# ── Feature flags ────────────────
ENABLE_FEATURE_X=true
```

Para usar JSON em vez de CSV: `ALLOWED_ORIGINS=["http://localhost","https://127.0.0.1:3000"]`.

---

## 4 ▪ Implementação (`app/core/config.py`)

```python
from __future__ import annotations
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import List, Any

from pydantic import BaseSettings, Field, field_validator
from pydantic_settings import SettingsConfigDict
from structlog import get_logger

from app.utils.git_info import get_git_sha  # ← util externo

logger = get_logger().bind(module="config")

# Decide quais env‑files ler (base + overlay)
_def_env_file = lambda env: (".env",) if env == "dev" else (".env", f".env.{env}")

class Settings(BaseSettings):
    # ── modo ─────────────────────
    environment: str = Field("dev", alias="ENVIRONMENT")
    debug: bool = Field(False, alias="DEBUG")
    testing: bool = Field(False, alias="TESTING")
    reload: bool = Field(False, alias="RELOAD")
    build_timestamp: str = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        alias="BUILD_TIMESTAMP",
    )

    # ── BD/cache ────────────────
    db_url: str | None = Field(None, alias="DB_URL")
    redis_url: str | None = Field(None, alias="REDIS_URL")

    # ── auth ────────────────────
    auth_secret_key: str = Field(..., alias="AUTH_SECRET_KEY")
    access_token_expire_min: int = Field(60 * 24, alias="ACCESS_TOKEN_EXPIRE_MIN")
    auth_algorithm: str = "HS256"

    # ── log ─────────────────────
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("plain", alias="LOG_FORMAT")

    # ── CORS ────────────────────
    allowed_origins: List[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")

    # ── extra ───────────────────
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")
    celery_broker_url: str | None = Field(None, alias="CELERY_BROKER_URL")
    enable_feature_x: bool = Field(False, alias="ENABLE_FEATURE_X")
    git_sha: str = Field(default_factory=lambda: os.getenv("GIT_SHA", get_git_sha()), alias="GIT_SHA")

    # Pydantic config
    model_config = SettingsConfigDict(
        env_file=_def_env_file(os.getenv("ENVIRONMENT", "dev")),
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=False,
        env_parse_json=False,   # ← evita json.loads automático
    )

    # Validators
    @field_validator("redis_url", mode="after")
    def _redis_required_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v

    @field_validator("allowed_origins", mode="before")
    def _parse_origins(cls, v: Any):
        if isinstance(v, str):
            return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v

@lru_cache
def get_settings() -> Settings:  # singleton
    return Settings()
```

### 📂 Novo utilitário `app/utils/git_info.py`

```python
import subprocess

def get_git_sha(short: bool = True) -> str:
    """Retorna o hash do commit ou 'unknown' se não estiver num repositório."""
    try:
        cmd = ["git", "rev-parse", "--short" if short else "HEAD"]
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
    except Exception:  # pragma: no cover
        return "unknown"
```

### 🚨 Validação de Ambiente e Segurança

A aplicação utiliza a biblioteca **Pydantic** para validar as variáveis de ambiente durante a inicialização, garantindo que:

* Todas as variáveis obrigatórias estejam presentes.
* Não existam variáveis desconhecidas.
* Seja realizado um fallback seguro, se aplicável.

---

## 5 ▪ Executando

```bash
# Dev (auto‑reload)
python run.py               # run.py usa settings.reload

# Testes
ENVIRONMENT=test pytest -q

# Prod local
ENVIRONMENT=prod python run.py
```

> `run.py` chama `uvicorn.run(..., reload=settings.reload)` — a flag vem do `.env`.

---

## 6 ▪ Ciclo de build & deploy

```
│ CI:  ENVIRONMENT=test.inmemory  → pytest
├── Exporta: GIT_SHA, BUILD_TIMESTAMP
└─► Docker build ARGs ─┐
                       │ imagem tagged com SHA
Prod: docker compose → env_file: .env  + .env.prod
```

### 🔄 Ciclo de desenvolvimento & deploy

```text
┌────────┐         ┌──────────────┐         ┌───────────────┐         ┌─────────┐
│ coder  │  git    │  GitHub CI   │  build  │  Registry/S3  │ deploy  │ Server  │
│ (dev)  │ ───────▶│  pytest      │ ───────▶│  docker image │ ───────▶│ prod    │
└────────┘         │  ENV=test    │         └───────────────┘         │ ENV=prod│
   ▲               │  ENV=test…   │                                    └─────────┘
   │               └──────────────┘
   │  uvicorn --reload (ENV=dev)
   └───────────────────────────────────────────────────────────────────────>
```

1. **Desenvolvimento local** – `uvicorn app.main:app --reload` (usa `.env`).
2. **Pull‑request** – GitHub Actions exporta `ENV=test` ou `test.inmemory`; roda `pytest`.
3. **Build** – pipeline gera imagem; secrets injetados em tempo de execução.
4. **Deploy** – `ENV=prod docker compose up -d` consome `.env` + `.env.prod`.

---

## 🚀 Executando a Aplicação por Ambiente

```bash
# Testes em memória (SQLite)
$env:ENVIRONMENT = "test.inmemory"

# Ambiente de teste
$env:ENVIRONMENT = "test"

# Ambiente de produção
$env:ENVIRONMENT = "prod"

# Rodar aplicação
uvicorn app.main:app --reload
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 🌱 O que essa abordagem habilita?

* **Isolamento** total de BD/Redis entre ambientes.
* **Segurança** – secrets nunca vão pro Git.
* **Feature‑flags** por ambiente (`settings.environment == "dev"`).
* **Rollback seguro** – basta mudar `ENV` para apontar outro arquivo.
* **CI turbo** com banco em memória, cortando minutos dos testes.

---

[⬅️ Voltar para o início](../README.md)
