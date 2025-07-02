# 🚀 Cache Redis para Melhor Desempenho

Este documento explica como o projeto **FastTrackAPI** utiliza o Redis para melhorar o desempenho e reduzir a latência de algumas requisições HTTP, com detalhes sobre implementação, funcionamento local e em container, testes e boas práticas.

---

## 🔄 Visão Geral

Utilizamos o padrão **cache-aside (lazy loading)**: o sistema tenta obter o resultado do Redis antes de consultar serviços externos ou realizar cálculos custosos. Se o valor não estiver no cache (MISS), ele é computado, armazenado no Redis e retornado.

| Fluxo da requisição        | Sem cache                          | Com cache Redis (cache-aside)                                          |
| -------------------------- | ---------------------------------- | ---------------------------------------------------------------------- |
| Execução                   | FastAPI → Serviço → DB/API externa | FastAPI → **Redis GET** → HIT ✔ (retorno rápido) / MISS ✖ → Serviço → Redis SETEX → Cliente |
| Latência média             | 400ms - 2s                         | 1ms - 5ms (após primeiro MISS)                                         |
| Carga externa              | 100% das requisições               | 1 requisição por TTL                                                   |

> **Estratégia**: *cache‑aside* (também chamado *lazy loading*) – apenas grava no Redis depois de consultar a fonte correta.

---

## ⚙️ Implementação no Código

| Camada                 | Arquivo / Elemento                              | Descrição                                                                                              |
| ---------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Provider**           | `app/deps.py → provide_redis()`                 | Cria **uma única** instância `Redis.from_url(..)` e a reaproveita em todo o app                        |
| **Decorator genérico** | `app/utils/cache.py → cached_json()`            | Função assíncrona que gera chave, consulta Redis (`GET`), serializa JSON (`SETEX`) e devolve resultado |
| **Aplicação real**     | `app/api/v1/endpoints/eventos.py`, entre outros | Endpoints decorados com `@cached_json("prefix", ttl)`                                                  |
| **Configuração**       | `.env / config.py → REDIS_URL`                  | Permite apontar para Redis local, Docker, ou nuvem  

### Decorador Genérico

Utilizamos o decorador `cached_json` que automatiza o uso do cache Redis com as seguintes etapas:

1. Geração de chave única com base nos parâmetros da requisição.
2. Verificação no Redis via `GET`.
3. Se não encontrar (MISS), executa a função original e armazena o resultado com `SETEX`.
4. Retorna o valor ao cliente.

Internamente, usamos `jsonable_encoder()` para garantir que o valor armazenado seja serializável e compatível com `response_model`.

Exemplo no código:

```python
@cached_json("local-info", ttl=86400)
async def obter_local_info(location_name: str, service: AbstractLocalInfoService = Depends(provide_local_info_service)):
    info = await service.get_by_name(location_name)
    if info is None:
        raise HTTPException(404, "Local não encontrado")
    return info
```

#### Correção de serialização

A serialização usa agora `jsonable_encoder` para transformar objetos Pydantic e tipos não-serializáveis:

```python
from fastapi.encoders import jsonable_encoder

serializable = jsonable_encoder(result)
await redis.setex(key, ttl, json.dumps(serializable))
```

E a leitura usa:

```python
cached = json.loads(raw)
return cached
```

##### 🔄 Patch atual do decorador `cached_json`

```python
try:
    if (raw := await redis.get(key)):
        logger.info("Cache hit", key=key)
        return json.loads(raw)

    logger.debug("Cache miss", key=key)
    result = await func(*args, **kwargs)
    serializable = jsonable_encoder(result)
    await redis.setex(key, ttl, json.dumps(serializable))
    return serializable
except Exception as e:
    logger.warning("Erro ao acessar o cache Redis", error=str(e))
    return await func(*args, **kwargs)
```

Removemos `default=str`, que convertia objetos em string literal e causava `ResponseValidationError` ao retornar do cache.

#### Geração de chave determinística

Ignoramos objetos como `repo`, `request`, `Session`, etc., ao construir a chave:

```python
SAFE_TYPES = (str, int, float, bool, type(None))
clean = {k: v for k, v in bound_args.items() if isinstance(v, SAFE_TYPES)}
key = prefix + ":" + str(hash(tuple(sorted(clean.items()))))
```

Evita que instâncias injetadas pelo FastAPI causem cache miss constante.

---

## 📍 Onde o Cache é Usado

| Endpoint                              | Prefixo / TTL      | Motivo                                           |
| ------------------------------------- | ------------------ | ------------------------------------------------ |
| `GET /api/v1/local_info`              | `local-info` / 24h | Geocodificação raramente muda                    |
| `GET /api/v1/forecast_info`           | `forecast` / 30min | API de clima é custosa e não muda rápido         |
| `GET /api/v1/eventos/top/soon`        | `top-soon` / 10s   | Ranking é volátil, mas leitura rápida é valiosa  |
| `GET /api/v1/eventos/top/most-viewed` | `top-viewed` / 30s | Muda apenas com `views++`; ideal para cache leve |

| Endpoint                              | Prefixo / TTL           | Motivo do cache                                                                               | Local do código                                        |
| ------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `GET /api/v1/local_info`              | `local‑info` / **24 h** | Resultado de geocodificação é praticamente estático; evita chamadas ao serviço externo.       | `app/api/v1/endpoints/eventos.py` → `obter_local_info` |
| `GET /api/v1/forecast_info`           | `forecast` / **30 min** | Chamada mockada mas, em produção, seria a API de clima (lenta/paga).                          | Mesmo arquivo → `obter_forecast_info`                  |
| `GET /api/v1/eventos/top/soon`        | `top‑soon` / **10 s**   | Ranking de "próximos N" muda a cada poucos segundos; snapshot ultra‑curto já satisfaz.        | Mesmo arquivo → `eventos_proximos`                     |
| `GET /api/v1/eventos/top/most-viewed` | `top‑viewed` / **30 s** | Ranking de mais vistos muda só quando views incrementa; 30 s equilibra frescor × performance. | Mesmo arquivo → `eventos_mais_vistos`                  |

Cada função é decorada com `@cached_json(<prefix>, ttl=<segundos>)`, implementado em **`app/utils/cache.py`**, que:

1. Gera uma chave determinística com prefixo + params;
2. Faz `await redis.get(key)` → **HIT** devolve JSON;
3. **MISS** executa a função real, serializa e grava `SETEX key ttl value`.

---

## ⚠️ Quando Não Usar Cache

| Razão                  | Justificativa                                                                    |
| ---------------------- | -------------------------------------------------------------------------------- |
| **Não idempotente**    | `POST`, `PUT`, `DELETE` alteram estado e não devem ser cacheados.                |
| **Alta cardinalidade** | Muitos parâmetros geram muitas combinações de chave (explosão de cache).         |
| **Dados voláteis**     | Quando o dado muda mais rápido do que o TTL possível.                            |
| **Privacidade**        | Respostas específicas por usuário não devem ser compartilhadas em cache anônimo. |

> Regra prática: cache apenas `GET`s idempotentes com acesso frequente e custo computacional alto.

---

## ✅ Benefícios

* **Redução drástica na latência:** Requisições comuns passam a ser respondidas em milissegundos.
* **Menor carga em serviços externos:** Reduz a frequência de chamadas custosas a APIs externas.
* **Escalabilidade facilitada:** Redis pode ser facilmente substituído por serviços gerenciados como AWS ElastiCache sem alteração no código.
* **Alta disponibilidade:** Caso o Redis falhe, o sistema continua funcionando normalmente, apenas ignorando o cache.

---

## 🗃️ Configuração do Redis

A variável `REDIS_URL` no `.env` define a URL de conexão, permitindo trocar de ambiente facilmente:

```ini
# .env (desenvolvimento local)
REDIS_URL=redis://localhost:6379/0

# .env.prod (ambiente com container)
REDIS_URL=redis://redis:6379/0
```

---

## ☑️ Checar Função de Geração de Key

A função de geração de chave utilizava todos os argumentos, incluindo objetos não serializáveis como repositórios, sessions, etc. Isso fazia com que o `hash()` resultasse em valores diferentes para chamadas idênticas.

### ✅ Solução

**Evite tipos não determinísticos na key:**

```python
def _make_key(prefix: str, bound_args: dict) -> str:
    SAFE_TYPES = (str, int, float, bool, type(None))
    clean = {k: v for k, v in bound_args.items() if isinstance(v, SAFE_TYPES)}
    return prefix + ":" + str(hash(tuple(sorted(clean.items()))))
```

Use no wrapper:

```python
bound = sig.bind_partial(*args, **kwargs)
bound.apply_defaults()
key = _make_key(prefix, bound.arguments)
```

### Versão parametrizável (include)

```python
def cached_json(prefix: str, ttl: int = 60, include: set[str] | None = None):
    ...
        key_args = {k: v for k, v in bound.arguments.items()
                    if (include and k in include) or
                       (include is None and isinstance(v, SAFE_TYPES))}
        key = _make_key(prefix, key_args)
```

No endpoint:

```python
@cached_json("top-soon", ttl=10, include={"limit"})
```

### Serialização correta do resultado

Em vez de usar `json.dumps(result, default=str)`, serialize com:

```python
from fastapi.encoders import jsonable_encoder
serializable = jsonable_encoder(result)
await redis.setex(key, ttl, json.dumps(serializable))
```

No cache hit:

```python
return json.loads(raw)
```

Evita erros como `ResponseValidationError` por strings onde o FastAPI espera dicionários.

---

## 🔪 Instalação (Desenvolvimento Local com Windows)

### 1. Instalação via Chocolatey

```powershell
choco install redis-64 -y
```

Esse comando instala o Memurai Developer (Redis compatível com Windows) e registra um serviço do Windows.

### 2. Controlar o serviço Redis (Memurai)

```powershell
Get-Service Memurai          # verificar status
Start-Service Memurai        # iniciar
Stop-Service Memurai         # parar
Set-Service Memurai -StartupType Automatic
```

### 2.1 Controlar o serviço Redis (Redis)

```powershell
Get-Service Redis            # verificar status
Start-Service Redis          # iniciar
Stop-Service  Redis          # parar
Set-Service   Redis -StartupType Automatic  # (ou Manual, Disabled…)
```

### 3. Executar manualmente (sem serviço)

```powershell
"C:\Program Files\Memurai\memurai.exe" --port 6379
```

Mantém a janela aberta ou use NSSM para rodar em background.

### 4. Testar se o Redis responde

```powershell
"C:\Program Files\Memurai\redis-cli.exe" -p 6379 ping
# deve responder: PONG
```

### 5. Verificar porta (opcional)

```powershell
netstat -ano | findstr ":6379"
```

### 6. Verificação no .env

```ini
REDIS_URL=redis://localhost:6379/0
```

Suba a API normalmente e verifique os logs:

* Primeira requisição: `MISS`
* Segunda requisição: `HIT`

### 7. Erros

#### Liberar locks quebrados
```powershell
# pare qualquer tarefa Chocolatey em background
Stop-Process -Name "choco*" -Force -ErrorAction SilentlyContinue
```

#### remova lock e pasta corrompida
```powershell
Remove-Item -Force -Recurse "C:\ProgramData\chocolatey\lib\9daa46124c4f3ddfd7a43a5d893196d2767a7cf7" -ErrorAction SilentlyContinue
Remove-Item -Force -Recurse "C:\ProgramData\chocolatey\lib-bad" -ErrorAction SilentlyContinue
(Se o primeiro caminho não existir mais, ignore o erro.)
```

---

## 🧪 Testes com Cache

| Caso de Teste        | Objetivo                                                      | Ferramenta sugerida             |
| -------------------- | ------------------------------------------------------------- | ------------------------------- |
| **HIT vs MISS**      | Verificar se a resposta vem do cache após primeira requisição | `fakeredis`, `pytest`           |
| **Expiração de TTL** | Confirmar renovação após TTL                                  | `time.sleep`, `freezegun`       |
| **Chaves únicas**    | Garantir que chaves são determinísticas                       | `redis.keys()`                  |
| **Falha do Redis**   | Verificar fallback se Redis estiver indisponível              | Mock/patch de `provide_redis()` |

Exemplo:

```python
from fastapi.encoders import jsonable_encoder

@cached_json("top-soon", ttl=10, include={"limit"})
async def eventos_proximos(limit: int = 5):
    ...
```

> Use `fakeredis.FakeRedis()` em testes para isolar dependência externa.

---

## 🔧 Boas Práticas

* Cache apenas rotas `GET` e com resultados relativamente estáticos.
* TTLs adaptados à natureza do dado (ex: 30s para ranking, 24h para dados estáticos).
* Sempre use `jsonable_encoder` antes de serializar com `json.dumps`.
* Gere chaves com base apenas em args simples
* Permita fallback (try/except no acesso Redis)

---

## 🧱 Redis: Funcionamento Local vs Container

### Por que Redis é externo?

O Redis é **um serviço separado**, não é parte do código Python. A aplicação apenas se conecta a ele por meio da biblioteca `redis.asyncio`.

Colocar o Redis dentro da própria API faria com que ele morresse e reiniciasse a cada deploy, além de perder os dados. Por isso, ele roda como processo separado ou container.

### 📦 Onde o Redis "vive"

| Cenário        | Binário redis-server       | Conexão FastAPI        | Iniciado via                   |
| -------------- | -------------------------- | ---------------------- | ------------------------------ |
| Dev Local      | Instalado via choco/brew   | `tcp://localhost:6379` | Serviço do sistema ou terminal |
| Docker Compose | Container `redis:7-alpine` | `tcp://redis:6379`     | `docker compose up`            |

Ambos os casos: o Redis é **um servidor real**, escutando em uma porta TCP. Não é uma thread nem subprocesso da API.

### 1. Fluxo sem container

```bash
┌───────────┐ 1) requisição
│ Navegador │──────────────►
└───────────┘               │
                            │     2) FastAPI usa cache
            ┌───────────────┴────────────┐
            │    FastAPI (processo)      │
            └─────────────────┬──────────┘
                              │ 3) socket TCP para 127.0.0.1:6379
                              ▼
                       ┌──────────────┐
                       │ redis-server │ (serviço no host)
                       └──────────────┘
```

### 2. Fluxo com Docker Compose

```
                           (rede Docker: backend)
┌───────────┐                       ▲
│ Navegador │──► 0.0.0.0:8000 ──────┘
└───────────┘
       host-network                       CONTAINERS
───────────────────────────────────────────────────────────
             │                        │
             ▼                        ▼
    ┌────────────────┐       ┌─────────────────┐
    │  api service   │──────▶│  redis service  │
    │ (fastapi:8000) │ TCP   │ (redis:6379)    │
    └────────────────┘       └─────────────────┘
```

* O Docker cria uma rede bridge e atribui hostnames.
* A URL redis\://redis:6379/0 aponta para o serviço Redis.
* Compose permite configurar restart, volumes e logs.

### 3. O que não mudou

| Componente               | Antes (host)           | Depois (container) |
| ------------------------ | ---------------------- | ------------------ |
| Cliente Redis            | `redis.asyncio`        | igual              |
| Função `provide_redis()` | REDIS\_URL (localhost) | REDIS\_URL (redis) |
| Decorator/cache          | `@cached_json`         | igual              |
| Código das rotas         | nada a mudar           | nada a mudar       |

### 4. Vantagens do container

* ✅ Reprodutibilidade: stack sobe com `docker compose up`.
* ✅ Isolamento: Redis não polui o sistema operacional.
* ✅ Orquestração: `depends_on`, healthcheck etc.
* ✅ Escalabilidade: fácil migrar para Redis gerenciado (ElastiCache etc.).

### 5. Pergunta frequente

**“O Redis está em outro processo?”**

> Sim. Seja local ou container, o Redis sempre roda em processo separado da API. FastAPI se conecta via TCP (localhost ou rede Docker).

---

✅ **TL;DR**: O Redis é um cache externo, operado fora da API. No desenvolvimento, pode rodar localmente como serviço do sistema. Em produção, containerizado, com o mesmo cliente e sem alterar o código. A chave para funcionar é ajustar corretamente a variável `REDIS_URL`.

---

## 🤖 Redis: Local vs Container

| Cenário            | Executável Redis                 | URL usada                  | Inicialização                      |
| ------------------ | -------------------------------- | -------------------------- | ---------------------------------- |
| **Antes** (local)  | `redis-server` no host (Memurai) | `redis://localhost:6379/0` | Manual via `Start-Service Memurai` |
| **Agora** (Docker) | container `redis:7-alpine`       | `redis://redis:6379/0`     | `docker-compose up`                |

Redis é sempre um processo separado (nunca uma thread Python).

---

## ⚙️ Trocar Redis por outro cache

1. Implemente `provide_memcached()` ou similar
2. Altere `cached_json` para usar outro client
3. Não é necessário alterar nenhum endpoint

---

---

---

## Checar função de gerar a key

O motivo clássico - e o seu código confirma - é que a função que gera a key
está incluindo objetos mutáveis/únicos (por ex. o repositório repo,
Session, etc.) nos args/kwargs.

python
Copiar
Editar
key = prefix + ":" + str(hash((args, tuple(sorted(kwargs.items())))))
Cada vez que FastAPI injeta repo, ele é uma nova instância
(<SQLEventRepo object at 0x...>).

O hash() desses objetos muda → a chave muda → MISS sempre.

1 — Verifique no log
Adicione, só para depurar, o valor da chave:

python
Copiar
Editar
logger.debug("Cache key", prefix=prefix, key=key)
Você verá algo como:

python-repl
Copiar
Editar
... key=top-soon:123456789
... key=top-soon:-987654321   # outra chamada → outra key
2 — Corrija a função de geração de chave
Abordagem simples: ignore parâmetros não cacheáveis
python
Copiar
Editar
def _make_key(prefix: str, bound_args: dict) -> str:
    SAFE_TYPES = (str, int, float, bool, type(None))
    clean = {k: v for k, v in bound_args.items() if isinstance(v, SAFE_TYPES)}
    return prefix + ":" + str(hash(tuple(sorted(clean.items()))))
E no wrapper:

python
Copiar
Editar
bound = sig.bind_partial(*args, **kwargs)
bound.apply_defaults()
key = _make_key(prefix, bound.arguments)
Não entram repo, service, request, nem qualquer objeto não
serializável.

Abordagem parametrizável
Se quiser algo mais explícito:

python
Copiar
Editar
def cached_json(prefix: str, ttl: int = 60, include: set[str] | None = None):
    ...
        key_args = {k: v for k, v in bound.arguments.items()
                    if (include and k in include) or
                       (include is None and isinstance(v, SAFE_TYPES))}
        key = _make_key(prefix, key_args)
Então no endpoint:

python
Copiar
Editar
@cached_json("top-soon", ttl=10, include={"limit"})

💡 O que ocorreu
Primeira requisição – cache miss

FastAPI devolve uma lista de objetos Pydantic (EventResponse).

No decorator você faz

python
Copiar
Editar
json.dumps(result, default=str)
Como EventResponse não é JSON-serializável, o default=str converte
cada objeto em string (a representação title='Evento 1' ...).

Segunda requisição – cache hit

Você lê o valor, faz json.loads(...) → volta uma lista de strings.

FastAPI tenta validar contra response_model=list[EventResponse]
→ vê string, não dicionário → levanta 10 erros “Input should be a valid
dictionary …”.

🛠️ Correção
Armazene no Redis um payload já serializado via
fastapi.encoders.jsonable_encoder, que transforma Pydantic, datetime,
Enum etc. em tipos puros JSON (dict, list, str, int).

python
Copiar
Editar
from fastapi.encoders import jsonable_encoder

...

serializable = jsonable_encoder(result)
await redis_client.setex(key, ttl, json.dumps(serializable))
return serializable      # devolve dict/list; FastAPI validará OK
E no cache hit basta:

python
Copiar
Editar
cached = json.loads(raw)
return cached            # FastAPI monta de volta o EventResponse
Patch completo (trecho do wrapper)
python
Copiar
Editar
try:
    if (raw := await redis_client.get(key)):
        logger.info("Cache hit", prefix=prefix, key=key)
        return json.loads(raw)

    logger.debug("Cache miss", prefix=prefix, key=key)
    result: T = await func(*args, **kwargs)

    serializable = jsonable_encoder(result)
    await redis_client.setex(key, ttl, json.dumps(serializable))
    logger.debug("Valor armazenado no cache", prefix=prefix, key=key, ttl=ttl)
    return serializable
Importante: remova default=str do json.dumps; ele “amassa” objetos
em string e perde estrutura.

---

[⬅️ Voltar para o README](../README.md)
