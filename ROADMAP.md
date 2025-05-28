# 📌 Roadmap Completo de Atualizações e Melhorias para o Projeto

Este documento descreve detalhadamente os próximos passos para o upgrade e aprimoramento do projeto backend FastAPI atual, detalhando cada tópico, vantagens e exemplos claros de implementação.

---

## 1. Dependências Reutilizáveis e Testáveis

### O que são dependências reutilizáveis?

No contexto do FastAPI, dependências são serviços, repositórios ou componentes que podem ser injetados em funções de rota. Torná-los reutilizáveis e testáveis significa desacoplar suas implementações concretas da lógica da aplicação, permitindo:

* Substituir facilmente por mocks em testes;
* Mudar a origem dos dados (ex: banco PostgreSQL por Redis) sem alterar o endpoint;
* Reaproveitar o mesmo contrato em diferentes partes do sistema.

### Vantagens

* **Testes unitários mais simples**: você pode simular dependências com facilidade.
* **Redução de acoplamento**: facilita refatoramentos e manutenção.
* **Inversão de dependência**: sua aplicação depende de contratos e não de implementações fixas.

---

### Como aplicar no Projeto Prisma

#### 1. Defina uma interface (contrato) usando `Protocol`

```python
# app/repositories/abstract_user.py
from typing import Protocol

class AbstractUserRepo(Protocol):
    async def get_by_id(self, user_id: int): ...
    async def list(self, *, role: str | None = None): ...
```

#### 2. Implemente uma versão real (ex: PostgreSQL, mock)

```python
# app/repositories/postgres_user.py
from app.repositories.abstract_user import AbstractUserRepo

class PostgresUserRepo(AbstractUserRepo):
    async def get_by_id(self, user_id: int):
        # consulta real ao banco
        pass
    async def list(self, role: str | None = None):
        pass
```

#### 3. Crie um provider que retorna a dependência

```python
# app/deps.py
from app.repositories.postgres_user import PostgresUserRepo

def provide_user_repo():
    return PostgresUserRepo()
```

#### 4. Injete nas rotas com `Depends`

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from app.repositories.abstract_user import AbstractUserRepo
from app.deps import provide_user_repo

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int, repo: AbstractUserRepo = Depends(provide_user_repo)):
    return await repo.get_by_id(user_id)
```

#### 5. Nos testes, sobrescreva facilmente:

```python
# tests/conftest.py ou em testes diretos
from app.main import app
from app.repositories.fakes import FakeUserRepo
from app.deps import provide_user_repo

app.dependency_overrides[provide_user_repo] = lambda: FakeUserRepo()
```

---

### Comparativo: Sem vs Com Inversão de Dependência

| Aspecto          | Sem Inversão                | Com Inversão (Protocol + Depends) |
| ---------------- | --------------------------- | --------------------------------- |
| Teste isolado    | Difícil (monkey patch, ifs) | Fácil (dependency override)       |
| Flexibilidade    | Acoplado ao banco direto    | Pode usar mocks, Redis etc.       |
| Reaproveitamento | Baixo                       | Alto                              |

---

### Considerações finais

Adotar dependências reutilizáveis e testáveis é um passo fundamental para tornar o código mais robusto, modular e preparado para testes. No Projeto Prisma, isso será aplicado progressivamente, começando pelos repositórios de usuários e eventos.

Essa abordagem está em linha com os princípios do SOLID (em especial, o Princípio da Inversão de Dependência) e prepara o backend para escalabilidade futura.


---

## 2. Configuração por Ambiente + Fallback Seguro

**O que é:** Gerenciar diferentes ambientes (dev, prod, test) com segurança.

**Vantagens:**

* Maior segurança e controle.
* Facilita a manutenção em diferentes ambientes.

**Implementação:**

* `.env`

```
ENVIRONMENT=dev
DB_URL=postgres://localhost/dev_db
```

* `.env.prod`

```
ENVIRONMENT=prod
DB_URL=postgres://prod_server/prod_db
```

* `.env.test`

```
ENVIRONMENT=test
DB_URL=postgres://localhost/test_db
```

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "dev"
    db_url: str

    model_config = Settings.ConfigDict(
        env_file=(".env", ".env.prod", ".env.test"),
        extra="forbid"
    )
```

4 ▪ Configuração por ambiente + fallback seguro
Estratégia recomendada

bash
Copiar
Editar
# raiz do projeto
.env         # default (dev)
.env.test    # CI/testes
.env.prod    # produção
Ajuste o Settings (Pydantic v2):

python
Copiar
Editar
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "dev"                # fallback
    db_url: str                             # obrigatória
    redis_url: str | None = None            # opcional

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod", ".env.test"),
        env_file_encoding="utf-8",
        extra="forbid",      # falha se variável desconhecida
        case_sensitive=False
    )
Fallback seguro para obrigatórias:

Declare sem valor-padrão (pydantic lançará ValidationError se faltar);

Ou forneça validator que lança exceção quando None (útil para variáveis que dependem de outras).

Docker Compose escolhe o arquivo certo:

yaml
Copiar
Editar
services:
  api:
    env_file:
      - .env
      - .env.${ENV:-dev}
Passe ENV=prod no pipeline de deploy.

---

## 3. Filtros e Paginação sem Banco

**O que é:** Implementar paginação e filtros diretamente em memória.

**Vantagens:**

* Melhora a performance.
* Permite testar a lógica antes de migrar para banco de dados.

**Implementação:**

```python
@router.get("/eventos")
def listar_eventos(skip: int = 0, limit: int = 10, cidade: str | None = None):
    eventos_filtrados = [evento for evento in eventos_db if cidade is None or evento["cidade"] == cidade]
    return eventos_filtrados[skip: skip + limit]
```

5 ▪ Filtros e paginação sem banco
Mesmo em estrutura in-memory (dict/list) você consegue:

python
Copiar
Editar
from fastapi import Query

@router.get("/eventos", response_model=list[EventOut])
def list_eventos(
    skip: int = Query(0, ge=0, description="Itens a pular"),
    limit: int = Query(20, le=100, description="Tamanho da página"),
    city: str | None = Query(None, description="Filtrar por cidade"),
):
    data = list(eventos_db.values())

    if city:
        data = [e for e in data if e.local_info.city == city]

    return data[skip: skip + limit]
Depois, ao migrar para SQLAlchemy, basta trocar a linha de consulta por query.offset(skip).limit(limit) — a assinatura da rota segue igual (princípio OCP).



---

## 4. Cache com Redis para Desempenho

**O que é:** Armazenar dados temporariamente para consultas rápidas.

**Vantagens:**

* Reduz a latência das requisições.
* Diminui carga sobre o backend e APIs externas.

**Implementação:**

```python
from redis.asyncio import Redis
redis = Redis.from_url("redis://localhost")

def cache(key: str, ttl: int):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if (result := await redis.get(key)):
                return json.loads(result)
            result = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@router.get("/forecast")
@cache("forecast", 1800)
async def get_forecast(city: str):
    return external_api.fetch_forecast(city)
```

Casos de uso imediatos no seu projeto
O que cachear	Como invalidar
ForecastInfo (API externa de clima)	TTL de 30 min ou até próxima chamada de background-task que atualiza previsões.
LocalInfo (API de geocodificação)	TTL 24 h; flush manual se usuário editar endereço.
Consultas “TOP N eventos”	TTL curto (p.ex. 5 s) – puro snapshot.

Integração passo a passo
Dep. no pyproject.toml:

toml
Copiar
Editar
[tool.poetry.dependencies]
aioredis = "^2.0"
Provider único:

python
Copiar
Editar
from redis.asyncio import Redis

async def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)
Wrapper de cache (exemplo simplificado):

python
Copiar
Editar
import json, functools
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T")

def cached_json(prefix: str, ttl: int = 60):
    def decorator(func: Callable[..., Awaitable[T]]):
        @functools.wraps(func)
        async def wrapper(*args, redis: Redis = Depends(get_redis), **kwargs):
            key = f"{prefix}:{args}:{kwargs}"
            if (cached := await redis.get(key)):
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator
Usar na rota de Forecast:

python
Copiar
Editar
@router.get("/forecast")
@cached_json("forecast", ttl=1800)        # 30 min
async def get_forecast(city: str):
    return await external_api.fetch_forecast(city)
Nenhum código da rota muda quando você trocar Redis por Memcached — só o provider.

---

## 5. Criar Pipeline GitHub Actions

**O que é:** Automatizar testes e deploys.

**Vantagens:**

* Testes automáticos.
* Feedback rápido sobre integrações e erros.

**Implementação:** `.github/workflows/ci.yml`

```yaml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      - name: Run Tests
        run: poetry run pytest --cov
```

---

## 6. Logs Estruturados

**O que é:** Logs detalhados e fáceis de analisar.

**Vantagens:**

* Maior facilidade de debug.
* Melhora a observabilidade da aplicação.

**Implementação:**

```python
from loguru import logger

logger.add("app.log", serialize=True)
logger.info("Evento criado", event_id=123)
```

---

## 7. Background Task para Previsão do Tempo

**O que é:** Execução assíncrona de tarefas.

**Vantagens:**

* Não bloqueia o usuário.
* Melhor experiência de uso.

**Implementação:**

```python
from fastapi import BackgroundTasks

async def atualizar_forecast(evento_id):
    forecast = await fetch_forecast()
    eventos_db[evento_id]["forecast"] = forecast

@router.post("/eventos")
def criar_evento(evento: Evento, tasks: BackgroundTasks):
    eventos_db[evento.id] = evento
    tasks.add_task(atualizar_forecast, evento.id)
```

---

\[...]

*(Continua com os demais tópicos detalhados)*

# 📌 Roadmap Completo de Atualizações e Melhorias para o Projeto

Este documento descreve detalhadamente os próximos passos para o upgrade e aprimoramento do projeto backend FastAPI atual, detalhando cada tópico, vantagens e exemplos claros de implementação.

---

## 1. Dependências Reutilizáveis e Testáveis

**O que é:** Permitir que componentes sejam facilmente substituídos, facilitando testes e manutenção.

**Vantagens:**

* Facilita testes unitários.
* Permite trocar implementações sem alterar a lógica principal.

**Implementação:**

*(veja no documento original)*

---

## 2. Configuração por Ambiente + Fallback Seguro

**O que é:** Gerenciar diferentes ambientes (dev, prod, test) com segurança.

**Vantagens:**

* Maior segurança e controle.
* Facilita a manutenção em diferentes ambientes.

**Implementação:**

*(veja no documento original)*

---

## 3. Filtros e Paginação sem Banco

**O que é:** Implementar paginação e filtros diretamente em memória.

**Vantagens:**

* Melhora a performance.
* Permite testar a lógica antes de migrar para banco de dados.

**Implementação:**

*(veja no documento original)*

---

## 4. Cache com Redis para Desempenho

**O que é:** Armazenar dados temporariamente para consultas rápidas.

**Vantagens:**

* Reduz a latência das requisições.
* Diminui carga sobre o backend e APIs externas.

**Implementação:**

*(veja no documento original)*

---

## 5. Criar Pipeline GitHub Actions

**O que é:** Automatizar testes e deploys.

**Vantagens:**

* Testes automáticos.
* Feedback rápido sobre integrações e erros.

**Implementação:**

*(veja no documento original)*

---

## 6. Logs Estruturados

**O que é:** Logs detalhados e fáceis de analisar.

**Vantagens:**

* Maior facilidade de debug.
* Melhora a observabilidade da aplicação.

**Implementação:**

*(veja no documento original)*

---

## 7. Background Task para Previsão do Tempo

**O que é:** Execução assíncrona de tarefas.

**Vantagens:**

* Não bloqueia o usuário.
* Melhor experiência de uso.

**Implementação:**

*(veja no documento original)*

---

## 8. Upload/Download de Arquivos & WebSockets (Opcional)

**O que é:** Permite interação em tempo real e troca de arquivos com o servidor.

**Vantagens:**

* Melhor experiência interativa.
* Facilita upload de arquivos para processamento.

**Implementação (Exemplo - Upload de eventos via planilha):**

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # Processar conteúdo da planilha
    return {"filename": file.filename}
```

---

## 9. Hardening de Segurança

**O que é:** Aumentar a segurança geral da aplicação.

**Vantagens:**

* Previne ataques comuns.
* Melhora segurança dos dados.

**Implementação:**

* Validação rigorosa de inputs com Pydantic.
* Middleware de segurança para CORS e Rate Limiting.
* Proteção JWT e headers seguros.

🔐 1. Hardening de Segurança
"Hardening" refere-se à prática de tornar uma aplicação mais segura, protegendo-a contra ataques e falhas que possam comprometer a confidencialidade, integridade ou disponibilidade dos dados.

No contexto FastAPI e aplicações Python backend, isso envolve:

🛡️ A. Validação e Sanitização de Entradas
Objetivo: Prevenir ataques comuns como SQL Injection, NoSQL Injection e XSS.

Como fazer:

Utilize o Pydantic (já em uso) rigorosamente.

Valide limites (comprimento, formato, caracteres permitidos).

Exemplo:

python
Copiar
Editar
from pydantic import BaseModel, constr

class UserInput(BaseModel):
    username: constr(regex="^[a-zA-Z0-9_-]{3,20}$")  # Regex para sanitização básica
    email: constr(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
🚫 B. Proteção contra ataques Cross-Origin (CORS)
Objetivo: Restringir quais sites podem acessar sua API.

Como fazer:

Instale o fastapi.middleware.cors.CORSMiddleware.

python
Copiar
Editar
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meusite.com.br"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
⏳ C. Rate Limiting
Objetivo: Evitar abusos (ataques DoS).

Como fazer:

Use uma lib como slowapi:

bash
Copiar
Editar
pip install slowapi
python
Copiar
Editar
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.get("/rota")
@limiter.limit("10/minute")  # Máximo 10 requisições por minuto por IP
async def minha_rota():
    return {"ok": True}
🗝️ D. Segurança de Tokens JWT
Objetivo: Garantir que tokens sejam seguros e expirem adequadamente.

Como fazer:

Usar chaves fortes e expiração curta.

python
Copiar
Editar
jwt.encode({"sub": user_id, "exp": expiration}, secret_key, algorithm="HS256")
Valide sempre a assinatura e validade (como você já fez).

🗄️ E. Banco de Dados Seguro
Objetivo: Evitar vazamentos.

Como fazer:

Use ORMs (SQLAlchemy) para evitar SQL Injection.

Não armazene senhas puras (já feito com passlib).

🔍 F. Segurança de Headers HTTP
Objetivo: Evitar ataques MITM (Man-in-the-middle).

Como fazer:

bash
Copiar
Editar
pip install secure
python
Copiar
Editar
from secure import SecureHeaders

secure_headers = SecureHeaders()

@app.middleware("http")
async def secure_headers_middleware(request, call_next):
    response = await call_next(request)
    secure_headers.fastapi(response)
    return response
🔐 Resumo prático de Hardening:
 Pydantic rigoroso para validar entradas

 Middleware CORS

 Middleware rate-limiting

 Segurança forte em JWT

 Headers HTTP seguros

---

## 10. Observabilidade Completa

**O que é:** Ter visibilidade detalhada do comportamento e performance da aplicação.

**Vantagens:**

* Diagnóstico rápido de problemas.
* Monitoramento eficiente do desempenho.

**Implementação:**

* Logs estruturados com Loguru.
* Métricas detalhadas com Prometheus e Grafana.
* Tracing com OpenTelemetry e Jaeger.

Observabilidade refere-se à capacidade de medir o estado interno do sistema, garantindo uma visão clara e precisa de sua operação, falhas e desempenho. É formada por três pilares principais:

Logs

Métricas

Tracing

📋 A. Logs Estruturados
Objetivo: Entender o comportamento histórico do sistema.

Ferramentas:

loguru (mais simples) ou structlog (mais avançado).

Exemplo com loguru:

python
Copiar
Editar
from loguru import logger

logger.add("file.log", rotation="500 MB", retention="10 days", serialize=True)

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Consultando usuário", user_id=user_id)
    return {"user": user_id}
📈 B. Métricas
Objetivo: Acompanhar desempenho e comportamento operacional.

Ferramentas: Prometheus + Grafana

Integração básica FastAPI com Prometheus:

bash
Copiar
Editar
pip install prometheus-fastapi-instrumentator
python
Copiar
Editar
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
O Prometheus coleta métricas e o Grafana as visualiza.

🔗 C. Tracing
Objetivo: Analisar o fluxo detalhado das requisições, identificando gargalos ou falhas.

Ferramentas: OpenTelemetry + Jaeger

Exemplo com OpenTelemetry:

bash
Copiar
Editar
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-instrumentation-fastapi
python
Copiar
Editar
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

FastAPIInstrumentor.instrument_app(app)
🚧 D. Middleware Global para Observabilidade
Um middleware para capturar erros e métricas de requisição automaticamente:

python
Copiar
Editar
@app.middleware("http")
async def logging_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info("Request completed", method=request.method, url=request.url.path, duration=duration, status=response.status_code)
    return response
🌐 Stack Recomendada para Observabilidade Completa:
Pilar	Ferramentas Recomendadas
Logs	Loguru, Structlog → Elastic Stack (ELK)
Métricas	Prometheus + Grafana
Tracing	OpenTelemetry + Jaeger

---

## 11. Princípios SOLID · DRY · KISS · YAGNI

**O que é:** Aplicação de boas práticas para código limpo e sustentável.

**Vantagens:**

* Código mais fácil de entender e manter.
* Redução de erros e retrabalho.

**Implementação:**

* Seguir rigorosamente revisão de código.
* Separar responsabilidades claras (SOLID).
* Evitar redundâncias e simplificar (DRY, KISS, YAGNI).

Princípio	O que significa no contexto FastAPI	Como aplicar agora
Single-Responsibility	Cada módulo/classe/função deve ter um motivo de mudança.	- Separe security.py em duas partes: jwt_service.py (gera/valida token) e password_hasher.py (hash/verify).
- Em eventos.py mova regras de negócio para services/event_service.py.
Open-Closed	Código aberto para extensão, fechado para modificação.	Exponha interfaces (p.ex. AbstractUserRepo) e injete a implementação concreta com Depends(...). Se trocar de Postgres para Mongo, basta registrar outro repo que implemente a mesma interface.
Liskov Substitution	Subclasses não devem quebrar contratos da superclasse.	Se você criar PremiumUser herdando de BaseUser, garanta que métodos como is_active() mantenham o comportamento esperado para qualquer rota que aceite BaseUser.
Interface Segregation	Interfaces pequenas, focadas.	Em vez de um repositório gigante com 30 métodos, divida em: UserQueryRepo (somente leitura) e UserCommandRepo (escrita). Rotas de consulta recebem só a interface de leitura, prevenindo importações desnecessárias.
Dependency Inversion	Dependa de abstrações, não de implementações.	Use from abc import ABC, abstractmethod para definir camadas Service ↔︎ Repository. Injete (com Depends) instâncias concretas só no startup ou em fábricas.
DRY	“Don’t Repeat Yourself”.	Gere erros padrão com um helper: raise_api_error(status=404, msg="Evento não encontrado").
Use pydantic.ConfigDict para repetir exemplos/descrições em vários esquemas.
KISS	“Keep It Simple, Stupid”.	Se o CRUD simples resolve, não adote CQRS + Event Sourcing agora. Use libs padrão do ecossistema antes de inventar algo próprio.
YAGNI	“You Aren’t Gonna Need It”.	Não adicione WebSockets porque “um dia talvez”. Só quando houver requisito real de push notifications.

Checklist rápido: cada arquivo deve responder “qual única responsabilidade eu cumpro?” — se hesitar, ele está fazendo coisa demais.

---

## 12. Docker e Docker Compose

**O que é:** Containerizar aplicações para melhor gerenciamento e portabilidade.

**Vantagens:**

* Facilita o deploy em diferentes ambientes.
* Reduz incompatibilidades e facilita escalabilidade.

**Implementação:**

* Verificar e atualizar Dockerfile e docker-compose com Redis e PostgreSQL configurados adequadamente.

---

## 13. Implementações Relativas ao Banco de Dados

**O que é:** Migração para persistência robusta de dados usando SQLAlchemy.

**Vantagens:**

* Garantia de integridade e consistência dos dados.
* Facilita consultas avançadas e complexas.

**Implementação:**

* Criar modelos ORM com SQLAlchemy.
* Gerenciar migrações usando Alembic.

---

## 14. Pontos adicionais pendentes

* Considerar implementação futura de WebSockets, dependendo da demanda.
* Aprimorar continuamente o gerenciamento de ambientes com práticas mais avançadas.

---

Este documento é um roadmap detalhado para organizar a evolução contínua e eficiente do seu projeto backend.
