# Em construção
# 🔧 Configuração por Ambiente

O projeto **FastTrackAPI** utiliza uma configuração organizada por ambientes para garantir segurança, flexibilidade e facilidade na manutenção. Cada ambiente possui um conjunto específico de configurações gerenciadas através de arquivos `.env` dedicados, facilitando o gerenciamento de variáveis sensíveis e específicas de cada contexto de execução.

---

## 🌱 Ambientes Disponíveis

O projeto suporta três ambientes principais:

* **Desenvolvimento (`dev`)**
* **Testes (`test`)**
* **Produção (`prod`)**

Cada ambiente é configurado através de arquivos específicos:

| Ambiente | Arquivo     | Quando usar                                            |
| -------- | ----------- | ------------------------------------------------------ |
| dev      | `.env`      | Desenvolvimento local (default)                        |
| test     | `.env.test` | Execução da suíte de testes e integração contínua (CI) |
| prod     | `.env.prod` | Deploy em produção                                     |

Gerenciamos **três ambientes padrão** — `dev`, `test` e `prod` — cada qual com seu próprio arquivo de variáveis:

| Arquivo     | Quando é lido                   | Exemplo de conteúdo                                             |
| ----------- | ------------------------------- | --------------------------------------------------------------- |
| `.env`      | Desenvolvimento local (default) | `ENVIRONMENT=dev`    `DB_URL=postgres://localhost/dev_db`       |
| `.env.test` | Execução da suíte *pytest*/CI   | `ENVIRONMENT=test`    `DB_URL=postgres://localhost/test_db`     |
| `.env.prod` | Deploy em produção              | `ENVIRONMENT=prod`    `DB_URL=postgres://postgres:5432/prod_db` |

> **Importante:** nunca commitamos segredos reais em `.env.prod`. Em produção as chaves vêm de *secret‑manager* ou de variáveis do host.

---

## 📦 Estrutura dos Arquivos `.env`

Cada arquivo de ambiente contém variáveis específicas, como:

```ini
# .env (desenvolvimento)
ENVIRONMENT=dev
DB_URL=postgresql://localhost/dev_db
REDIS_URL=redis://localhost:6379/0
AUTH_SECRET_KEY=supersecretdevkey
```

```ini
# .env.test (testes)
ENVIRONMENT=test
DB_URL=postgresql://localhost/test_db
REDIS_URL=redis://localhost:6379/1
AUTH_SECRET_KEY=supersecrettestkey
```

```ini
# .env.prod (produção)
ENVIRONMENT=prod
DB_URL=postgresql://postgres:5432/prod_db
REDIS_URL=redis://redis:6379/0
AUTH_SECRET_KEY=supersecretprodkey
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

## 🚀 Executando a Aplicação por Ambiente

### Desenvolvimento (default)

```bash
uvicorn app.main:app --reload
```

### Testes

```bash
ENV=test pytest -q
```

### Produção (simulação local)

```bash
ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Onde está implementado

* `app/core/config.py` – classe **`Settings`** (Pydantic v2) lê todas as variáveis:

  * `environment`, `db_url`, `redis_url`, `auth_secret_key`, etc.
  * `model_config` define `env_file=(".env", ".env.prod", ".env.test")`, `extra="forbid"` e `case_sensitive=False`.
  * Validação extra `@field_validator("redis_url")` obriga Redis em `prod`.
  * Função `get_settings()` com `@lru_cache` garante leitura uma única vez.

Estrutura resumida (trecho):

```python
class Settings(BaseSettings):
    environment: str = Field("dev", alias="ENVIRONMENT")  # fallback → dev
    db_url: str = Field(..., alias="DB_URL")
    redis_url: str | None = Field(None, alias="REDIS_URL")
    auth_secret_key: str = Field(..., alias="AUTH_SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod", ".env.test"),
        extra="forbid",
    )

    @field_validator("redis_url", mode="after")
    def require_redis_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v
```

### Como trocar de ambiente sem Docker

```bash
# Desenvolvimento (default)
uvicorn app.main:app --reload

# Testes/CI
ENV=test pytest -q           # usa .env.test

# Simular produção local
ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Possibilidades habilitadas pela abordagem

* **Isolamento total** de bases de dados/serviços entre `dev`, `test` e `prod`.
* **Fail‑fast**: variáveis desconhecidas ou obrigatórias ausentes derrubam a app no start.
* **Feature flags** por ambiente (ex.: ativar um provider ou log extra só em `dev`).
* **Secrets seguros** em produção, lidos do ambiente/container, nunca versionados.
* **Deploy simples**: `ENV=prod docker compose up -d` carrega `.env` + `.env.prod`.

---

## Divisão dos ambientes

# 3.1 — DEV  (é o default – pode até omitir)
uvicorn app.main:app --reload
# ou
ENV=dev uvicorn app.main:app --reload


# 3.2 — TESTE  (útil p/ CI/local)
ENV=test pytest -q                       # carrega .env.test
# ou, se quiser subir a API no modo test:
ENV=test uvicorn app.main:app


# 3.3 — PRODUÇÃO  (simulação local)
ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 8000

---

[⬅️ Voltar para o início](../README.md)
