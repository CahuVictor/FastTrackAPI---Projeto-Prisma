# Em construção
# 🔧 Configuração por Ambiente

O projeto **FastTrackAPI** utiliza uma configuração organizada por ambientes para garantir segurança, flexibilidade e facilidade na manutenção. Cada ambiente possui um conjunto específico de configurações gerenciadas através de arquivos `.env` dedicados, facilitando o gerenciamento de variáveis sensíveis e específicas de cada contexto de execução.

---

## 🔐 Configuração por Ambiente + Fallback Seguro

A aplicação roda em *quatro* sabores de execução – **dev**, **test**, **test.inmemory** e **prod** – cada um com o *seu* arquivo `.env`.

### ✨ Por que separar ambientes?

| Ambiente          | Objetivo                                                | O que normalmente muda                                                                                               |
| ----------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **dev**           | Trabalho diário do dev, auto‑reload, logs verbosos.     | BD local (`postgres://localhost/dev_db`), Redis local, segredos fictícios.                                           |
| **test**          | Rodar **pytest** & CI com banco isolado.                | BD separado (`postgres://localhost/test_db`), possivelmente Redis **desligado**; mocks substituem serviços externos. |
| **test.inmemory** | Executar testes ultra‑rápidos *in‑memory* sem Postgres. | `DB_URL=sqlite:///:memory:` → elimina I/O, acelera pipeline.                                                         |
| **prod**          | Atender usuários reais.                                 | Hostnames internos (ex.: `postgres.internal`), segredos vindos de Secret‑Manager, logs estruturados `INFO`.          |

> **Dev ≠ Test.**  A suíte de testes deve poder destruir dados sem bagunçar seu banco de desenvolvimento.

### 📄 Arquivos `.env`

| Arquivo              | Quando é lido       | Exemplo mínimo                                                |
| -------------------- | ------------------- | ------------------------------------------------------------- |
| `.env`               | default/dev         | `ENVIRONMENT=dev`  `DB_URL=postgres://localhost/dev_db`       |
| `.env.test`          | `ENV=test`          | `ENVIRONMENT=test`  `DB_URL=postgres://localhost/test_db`     |
| `.env.test.inmemory` | `ENV=test.inmemory` | `ENVIRONMENT=test.inmemory`  `DB_URL=sqlite:///:memory:`      |
| `.env.prod`          | `ENV=prod`          | `ENVIRONMENT=prod`  `DB_URL=postgres://postgres:5432/prod_db` |

**Nunca** commite segredos reais em `.env.prod`; use variáveis do host ou Secret‑Manager.

---

## 📦 Estrutura dos Arquivos `.env`

Cada arquivo de ambiente contém variáveis específicas, como:

```ini
# .env (desenvolvimento)
ENVIRONMENT=dev
AUTH_SECRET_KEY=dev-super-secret
DB_URL=postgresql://prisma:prisma123@localhost:5432/prisma_db
DATABASE_URL=postgresql://prisma:prisma123@localhost:5432/prisma_db
REDIS_URL=redis://localhost:6379/0
```

```ini
# .env.test (testes)
ENVIRONMENT=test
AUTH_SECRET_KEY=test-secret
DATABASE_URL=postgresql://user:password@db:5432/prisma
SECRET_KEY=your_secret_key
```

```ini
# .env.test.inmemory (testes)
ENVIRONMENT=test.inmemory
AUTH_SECRET_KEY=test-inmemory-secret
DATABASE_URL=sqlite:///:memory:
```

```ini
# .env.prod (produção)
ENVIRONMENT=prod
AUTH_SECRET_KEY=${PRISMA_AUTH_SECRET_KEY}
REDIS_URL=redis://redis:6379/0
```

---

## 🚨 Validação de Ambiente e Segurança

A aplicação utiliza a biblioteca **Pydantic** para validar as variáveis de ambiente durante a inicialização, garantindo que:

* Todas as variáveis obrigatórias estejam presentes.
* Não existam variáveis desconhecidas.
* Seja realizado um fallback seguro, se aplicável.

### Exemplo de Configuração com Pydantic

O arquivo `app/core/config.py` gerencia a leitura e validação dos ambientes:

```python
from pydantic import BaseSettings, Field, field_validator
from functools import lru_cache

class Settings(BaseSettings):
    environment: str = Field("dev", alias="ENVIRONMENT")
    db_url: str = Field(..., alias="DB_URL")
    redis_url: str | None = Field(None, alias="REDIS_URL")
    auth_secret_key: str = Field(..., alias="AUTH_SECRET_KEY")

    model_config = {
        "env_file": (".env", ".env.prod", ".env.test"),
        "extra": "forbid",
    }

    @field_validator("redis_url", mode="after")
    def require_redis_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v

@lru_cache
def get_settings():
    return Settings()
```

---

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
# Desenvolvimento (default)
uvicorn app.main:app --reload

# Testes (Postgres)
ENV=test pytest -q

# Testes em memória (SQLite)
ENV=test.inmemory pytest -q

# Produção local
ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 🌱 O que essa abordagem habilita?

* **Isolamento** total de BD/Redis entre ambientes.
* **Segurança** – secrets nunca vão pro Git.
* **Feature‑flags** por ambiente (`settings.environment == "dev"`).
* **Rollback seguro** – basta mudar `ENV` para apontar outro arquivo.
* **CI turbo** com banco em memória, cortando minutos dos testes.

---

[⬅️ Voltar para o início](../README.md)
