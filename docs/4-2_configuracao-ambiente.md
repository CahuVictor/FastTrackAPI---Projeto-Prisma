# 🔧 Configuração por Ambiente + Fallback Seguro

> Documento focado apenas em **Settings /.env** e tratamento de erros de configuração. Para visão geral do projeto, veja o README.

---

## 1 ▪ Por que separar ambientes?

| Ambiente          | Objetivo                                           | O que muda                                                   |
| ----------------- | -------------------------------------------------- | ------------------------------------------------------------ |
| **dev**           | Trabalho diário com *auto‑reload* e logs verbosos. | Postgres/Redis locais, segredos fictícios.                   |
| **test**          | `pytest` + CI usando Postgres.                     | Banco isolado, Redis mock/fora.                              |
| **test.inmemory** | Testes ultra‑rápidos em RAM.                       | `DB_URL=sqlite:///:memory:` (zero I/O).                      |
| **prod**          | Servir usuários reais.                             | Hostnames internos, segredos em Secret‑Manager, logs `INFO`. |

> **Dev ≠ Test** – a suíte de testes deve poder destruir dados sem afetar seu BD local.

---

## 2 ▪ Arquivos `.env`

| Arquivo              | Quando é lido       | Exemplo mínimo                                           |
| -------------------- | ------------------- | -------------------------------------------------------- |
| `.env`               | default/dev         | `ENVIRONMENT=dev`  `DB_URL=postgres://localhost/dev_db`  |
| `.env.test`          | `ENV=test`          | `ENVIRONMENT=test` `DB_URL=postgres://localhost/test_db` |
| `.env.test.inmemory` | `ENV=test.inmemory` | `DB_URL=sqlite:///:memory:`                              |
| `.env.prod`          | `ENV=prod`          | `DB_URL=postgres://postgres/prod_db`                     |

Segredos de produção **nunca** são commitados – use variáveis do host ou Secret‑Manager.

---

## 3 ▪ Exemplo completo de `.env` (dev)

```ini
# ── Modo ─────────────────────────
ENVIRONMENT=dev
DEBUG=true
TESTING=false
RELOAD=true

# ── Build info (gerado se ausente, ISO‑8601 em **UTC**) ─
# Usamos timezone UTC para que a data seja consistente em qualquer máquina (dev, CI ou produção).
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
# opcional JSON → ALLOWED_ORIGINS=["http://localhost","https://127.0.0.1:3000"]

# ── Filas / tarefas ──────────────
CELERY_BROKER_URL=redis://redis:6379/1

# ── Feature flags ────────────────
ENABLE_FEATURE_X=true
```

Para usar JSON em vez de CSV: `ALLOWED_ORIGINS=["http://localhost","https://127.0.0.1:3000"]`.

---

## 4 ▪ Implementação principal (`app/core/config.py`)

```python
from __future__ import annotations
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import List, Any

from pydantic import BaseSettings, Field, field_validator
from pydantic_settings import SettingsConfigDict
from structlog import get_logger

from app.utils.git_info import get_git_sha

logger = get_logger().bind(module="config")

# Escolhe arquivos: base + overlay do ENVIRONMENT
_env_files = lambda env: (".env",) if env == "dev" else (".env", f".env.{env}")

class Settings(BaseSettings):
    # ── modo ─
    environment: str = Field("dev", alias="ENVIRONMENT")
    debug: bool = Field(False, alias="DEBUG")
    testing: bool = Field(False, alias="TESTING")
    reload: bool = Field(False, alias="RELOAD")
    build_timestamp: str = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        alias="BUILD_TIMESTAMP",
    )

    # ── BD/cache ─
    db_url: str | None = Field(None, alias="DB_URL")
    redis_url: str | None = Field(None, alias="REDIS_URL")

    # ── auth ─
    auth_secret_key: str | None = Field(None, alias="AUTH_SECRET_KEY")
    access_token_expire_min: int = Field(60 * 24, alias="ACCESS_TOKEN_EXPIRE_MIN")
    auth_algorithm: str = "HS256"

    # ── log ─
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("plain", alias="LOG_FORMAT")

    # ── CORS ─
    allowed_origins: List[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")

    # ── extras ─
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")
    celery_broker_url: str | None = Field(None, alias="CELERY_BROKER_URL")
    enable_feature_x: bool = Field(False, alias="ENABLE_FEATURE_X")
    git_sha: str = Field(default_factory=lambda: os.getenv("GIT_SHA", get_git_sha()), alias="GIT_SHA")

    # Config Pydantic
    model_config = SettingsConfigDict(
        env_file=_env_files(os.getenv("ENVIRONMENT", "dev")),
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=False,
        env_parse_json=False,  # evita tentativa de json.loads em strings
    )

    # Validadores
    @field_validator("redis_url", mode="after")
    def _redis_required_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v

    @field_validator("auth_secret_key", mode="after")
    def _key_required_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("AUTH_SECRET_KEY é obrigatório em produção")
        return v

    @field_validator("allowed_origins", mode="before")
    def _parse_origins(cls, v: Any):
        if isinstance(v, str):  # CSV -> list
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


# Singleton + tratamento de erros amigável
from pydantic import ValidationError
from app.utils.settings_error import abort_with_validation_errors

@lru_cache
def get_settings() -> Settings:
    try:
        s = Settings()
        logger.info("Settings carregado", env=s.environment)
        return s
    except ValidationError as exc:  # imprime tabela e encerra
        abort_with_validation_errors(exc)
```

### 📂 Utils auxiliares

* `app/utils/git_info.py` – gera `git_sha`
* `app/utils/settings_error.py` – imprime erros de validação em tabela Rich (ou texto simples) e encerra.

---

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

# Testes (Postgres)
ENVIRONMENT=test pytest -q

# Testes em memória
ENVIRONMENT=test.inmemory pytest -q

# Prod local
ENVIRONMENT=prod python run.py
```

> `run.py` chama `uvicorn.run(..., reload=settings.reload)` — a flag vem do `.env`.

---

## 6 ▪ Pipeline - Ciclo de build & deploy (resumo)

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

## 7 ▪ Mensagens de erro amigáveis

* Variáveis desconhecidas ou ausentes disparam `ValidationError`.
* O wrapper em `get_settings()` usa **Rich** para exibir tabela:

```
🚫  Configuração de ambiente inválida
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Campo        ┃ Problema                       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ redis_url    │ REDIS_URL é obrigatório em produção │
└──────────────┴────────────────────────────────┘
```

Se Rich não estiver instalado, mostra texto simples e finaliza com `exit(1)`.

---

### 🌱 O que essa abordagem habilita?

* **Isolamento** total de BD/Redis entre ambientes.
* **Segurança** – secrets nunca vão pro Git.
* **Feature‑flags** por ambiente (`settings.environment == "dev"`).
* **Rollback seguro** – basta mudar `ENV` para apontar outro arquivo.
* **CI turbo** com banco em memória, cortando minutos dos testes.

---

[⬅️ Voltar para o início](../README.md)
