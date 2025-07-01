# Em construção
# 🚀 Cache com Redis para Melhor Desempenho

Este documento descreve como o projeto FastTrackAPI utiliza o Redis para melhorar significativamente o desempenho das requisições HTTP, reduzindo latência e carga sobre serviços externos e bancos de dados. Utilizamos o padrão **cache-aside** (também conhecido como lazy loading), que verifica o cache antes de consultar serviços externos ou realizar operações custosas.

---

## 🔄 Visão Geral

| Aspecto             | Sem cache                             | Com Redis (cache-aside)                                                           |
| ------------------- | ------------------------------------- | --------------------------------------------------------------------------------- |
| Fluxo da requisição | FastAPI → Serviço → Banco/API externa | FastAPI → **Redis GET** → HIT ✔ (retorno rápido) / MISS ✖ → Serviço → Redis SETEX |
| Latência média      | 400ms a 2s (dependendo da origem)     | 1ms a 5ms após primeiro MISS                                                      |
| Carga externa       | 100% das requisições                  | 1 requisição por TTL                                                              |

|                                |  Sem cache                                                  |  Com Redis (cache‑aside)                                                                                                |
| ------------------------------ | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Fluxo de requisição            | FastAPI → Service → API externa ou consulta lenta → Cliente | FastAPI → **Redis GET** → *HIT*? ✔ devolve em ◉ ms / *MISS* ✖ → Service → API externa → **Redis SETEX** (TTL) → Cliente |
| Latência média                 |  100–800 ms                                                 |  ≈1–5 ms após o primeiro acesso                                                                                         |
| Carga no backend/API terceiros | 100 % das requisições                                       | 1 requisição a cada *TTL*                                                                                               |

**Estratégia:** usamos o padrão *cache‑aside* (comumente chamado read‑through): a própria aplicação consulta o cache antes de executar a operação cara e grava o resultado quando não encontra a chave.

|               |  Sem cache                                      |  Com Redis (cache‑aside)                                                                                            |
| ------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Fluxo         | FastAPI → Service → API externa/banco → Cliente | FastAPI → **Redis GET** → *HIT*? ✔ devolve em 1‑5 ms / *MISS* ✖ → Service → API externa → **Redis SETEX** → Cliente |
| Latência      | 400 ms – 2 s (dependendo da origem)             | 1 ‑ 5 ms após primeiro MISS                                                                                         |
| Carga externa | 100 % das requests                              | ≃ 1 request por TTL                                                                                                 |

> **Estratégia**: *cache‑aside* (também chamado *lazy loading*) – apenas grava no Redis depois de consultar a fonte correta.

---

## ⚙️ Implementação no Código

|  Camada                |  Arquivo / Elemento                                                                                                     |  Descrição                                                                                              |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Provider**           | `app/deps.py → provide_redis()`                                                                                         | Cria  **uma única** instância `Redis.from_url(..)`  e a reaproveita em todo o app                       |
| **Decorator genérico** | `app/utils/cache.py → cached_json()`                                                                                    | Função assíncrona que gera chave, consulta Redis (`GET`), serializa JSON (`SETEX`) e devolve resultado  |
| **Aplicação real**     | `app/api/v1/endpoints/local_info.py` <br>`app/api/v1/endpoints/forecast_info.py` <br>`app/api/v1/endpoints/eventos.py`  | Endpoints decorados com `@cached_json("prefix", ttl)`                                                   |
| **Configuração**       | `.env / config.py → REDIS_URL`                                                                                          | Permite apontar para Redis local, Docker, ou nuvem                                                      |

### Decorador Genérico

Utilizamos um decorador genérico, `cached_json`, que automatiza todo o processo:

* Gera uma chave única para cada requisição.
* Verifica se o resultado já existe no cache (Redis GET).
* Caso contrário (MISS), chama o serviço original, armazena o resultado (Redis SETEX) e retorna ao cliente.

Exemplo no código:

```python
@cached_json("local-info", ttl=86400)
async def obter_local_info(location_name: str, service: AbstractLocalInfoService = Depends(provide_local_info_service)):
    info = await service.get_by_name(location_name)
    if info is None:
        raise HTTPException(404, "Local não encontrado")
    return info
```

### 4.2 Onde o cache está sendo usado no código

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

### 4.3 Por que *não* aplicamos cache em todas as rotas?

| Razão                       | Explicação                                                                                                                  | Exemplo no projeto                                                                      |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Não idempotente**         | Rotas `POST`, `PUT`, `PATCH`, `DELETE` alteram estado. Cachear pode devolver versão desatualizada ou atrapalhar validações. | `POST /api/v1/eventos` cria evento; *não cacheamos*.                                    |
| **Alta cardinalidade**      | Muitas combinações de query‑params criam milhões de chaves ("key‑explosion").                                               | `GET /api/v1/eventos?skip&limit&city` – cada página e cidade seria uma chave diferente. |
| **Dados voláteis**          | Conteúdo muda mais rápido que um TTL razoável, tornando o cache inútil.                                                     | Se tivéssemos um endpoint "/metricas/tempo‑real" não faria sentido cachear.             |
| **Segurança e privacidade** | Respostas personalizadas por usuário não devem ser compartilhadas entre sessões anônimas.                                   | Rotas de autenticação e perfis de usuário ficam fora do cache.                          |

> **Regra prática**: cache apenas `GET`s idempotentes, requisitados com alta frequência **e** cujo custo de geração é maior que 1‑2 ms. Mantenha o restante simples para evitar inconsistências.

---

## 🗃️ Configuração do Redis

A URL do Redis é configurada via variável de ambiente, permitindo flexibilidade entre ambientes:

```ini
# .env
REDIS_URL=redis://localhost:6379/0

# .env.prod
REDIS_URL=redis://redis:6379/0
```

---

## ✅ Benefícios

* **Redução drástica na latência:** Requisições comuns passam a ser respondidas em milissegundos.
* **Menor carga em serviços externos:** Reduz a frequência de chamadas custosas a APIs externas.
* **Escalabilidade facilitada:** Redis pode ser facilmente substituído por serviços gerenciados como AWS ElastiCache sem alteração no código.
* **Alta disponibilidade:** Caso o Redis falhe, o sistema continua funcionando normalmente, apenas ignorando o cache.

---

## 4.5 Onde alterar caso troque Redis por outro cache

1. Implemente novo provider (`provide_memcached`, por ex.) no mesmo formato.
2. Altere `cached_json` para usar esse provider.
3. Nenhuma rota precisa ser tocada – o decorator cuida de tudo.

---

**TL;DR:** adicionamos Redis para reduzir latência e carga sobre APIs externas com um decorator plug‑and‑play; a própria estrutura permite testar HIT/MISS, TTL e resiliência sem rodar Redis de verdade.

---

## 🧪 Testes com Cache

Testes essenciais que podem ser realizados:

* **HIT vs MISS:** Garantir que a segunda requisição retorna imediatamente do cache.
* **Expiração de TTL:** Confirmar que após o tempo configurado, o cache expira e busca novamente.
* **Falha de Redis:** O sistema não deve falhar; apenas opera sem cache.

|  Caso de teste                   |  Objetivo                                                                           |  Ferramentas sugeridas                               |
| -------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **Cache HIT vs MISS**            | Garantir que a primeira requisição (MISS) chama o service/DB e a segunda (HIT) não  | `fakeredis` + pytest → verificar contadores / spies  |
| **TTL expira**                   | Após `ttl` segundos, o decorator deve buscar dados novamente                        | `freezegun` ou `time.sleep` curto                    |
| **Chave única**                  | Requisições com parâmetros diferentes devem gerar chaves diferentes                 | Asset `redis.keys()` contém os hashes esperados      |
| **Fallback se Redis fora do ar** | A aplicação não pode quebrar: decorator executa função original                     | Mock `provide_redis` para levantar `ConnectionError` |

>  **Observação:** nenhum teste precisa de Redis real; use `fakeredis.FakeRedis` e faça override de `provide_redis`.

Exemplo de teste com `fakeredis`:

```python
async def test_cache_hit(client, fake_redis):
    resp1 = await client.get("/api/v1/local_info?location_name=recife")
    assert resp1.status_code == 200

    resp2 = await client.get("/api/v1/local_info?location_name=recife")
    assert resp2.json() == resp1.json()
```

1. **HIT × MISS** — invoque o endpoint duas vezes; a segunda deve ser mais rápida e não acionar o service.
2. **TTL** — após expirar, a próxima chamada volta a ser MISS.
3. **Key uniqueness** — parâmetros diferentes geram chaves diferentes e não se sobrepõem.
4. **Fallback se Redis cair** — simule `ConnectionError` (monkeypatch em `provide_redis`) e verifique que o endpoint ainda responde, só que sem cache.
5. **Isolamento em testes** — use `fakeredis` via override de `provide_redis` para evitar side‑effects.

```python
# exemplo de teste HIT/MISS com fakeredis
async def test_cache_hit(client, fake_redis):
    resp1 = await client.get("/api/v1/local_info?location_name=recife")
    assert resp1.status_code == 200

    # segunda chamada deve vir do cache
    resp2 = await client.get("/api/v1/local_info?location_name=recife")
    assert resp2.json() == resp1.json()
    # opcional: use fake_redis.get(key) para confirmar presença do valor
```

---

## 🔧 Boas Práticas

* Utilize cache apenas em rotas idempotentes (`GET`) e com resultados relativamente estáticos.
* Configure TTL apropriado para cada tipo de dado (exemplo: previsão do tempo em 30 minutos, geocodificação em 24 horas).
* Garanta que as chaves sejam determinísticas e únicas por parâmetros para evitar colisões e inconsistências.

\* **TTL adequado** → previsão do tempo 30 min; geocodificação 24 h; rankings de eventos 5–30 s.
\* **Chave determinística** → `prefix` + `hash(args, kwargs)` – minimiza colisões e simplifica invalidar.
\* **Fallback gracioso** → Se Redis cair, o decorator só ignora o cache.
\* **Serialização única** → Sempre JSON string (`default=str`) para uniformidade.

---

📦 Onde o Redis “vive” – antes × depois
Cenário	Onde está o binário redis-server?	Como o FastAPI se conecta?	Como é iniciado/parado?
Antes (dev local)	Instalado na máquina host via brew, apt, choco…	tcp://localhost:6379
(loopback da própria máquina)	redis-server rodava como processo separado/serviço do SO (systemd, serviço do Windows) – você mesmo ligava/desligava.
Depois (Docker Compose)	Dentro de um container chamado redis (imagem redis:7-alpine)	tcp://redis:6379
(nome-DNS do serviço na rede Docker)	docker compose up cria outro processo isolado no container; down remove. Uptime, logs e rede gerenciados pelo Docker.

Em ambos os casos o Redis é sempre um servidor próprio, 100 % fora
do processo Python. Não é “outra thread” do FastAPI – é um executável C que
escuta numa porta TCP.

1. Como era o fluxo “sem container”
bash
Copiar
Editar
┌───────────┐ 1) requer /local_info
│ Navegador │──────────────►
└───────────┘               │
                            │     2) chama decorator
            ┌───────────────┴────────────┐
            │    FastAPI  (processo)     │
            └─────────────────┬──────────┘
                              │ 3) socket TCP 127.0.0.1:6379
                              ▼
                       ┌──────────────┐
                       │ redis-server │  (processo do host, fora do docker)
                       └──────────────┘
Instalação manual – brew install redis

Iniciado em background (brew services start redis)

FastAPI resolve localhost, abre um socket, fala RESP.

2. Como ficou “com Docker Compose”
markdown
Copiar
Editar
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
Imagem oficial – redis:7-alpine

Declarado em docker-compose.yml.

O Docker cria uma bridge network (backend).

Cada serviço recebe um hostname – aqui api e redis.

O FastAPI acessa redis:6379 (DNS interno).

Logs, restart-policy, snapshot-volume podem ser configurados no YAML.

3. O que não mudou
Componente	Antes	Depois
Biblioteca cliente	redis.asyncio	igual
Função provide_redis()	lê REDIS_URL	igual (agora redis://redis:6379/0)
Decorators/cache	@cached_json	idêntico
Código das rotas	nada a tocar	nada a tocar

Ou seja: só deslocamos o servidor do “host” para “container”, trocando
localhost por redis na URL – o restante continua transparente.

4. Por que containerizar é melhor
Reprodutibilidade – qualquer máquina com Docker sobe a stack
completa; não há “funciona-na-minha-máquina”.

Isolamento – libs do Redis não “poluem” o host; porta 6379 não
fica escancarada para todo o PC se você não quiser.

Orquestração – depends_on garante que o backend só inicie após
o Redis passar no healthcheck (redis-cli ping).

Escalabilidade – em produção você pode ter múltiplos containers
FastAPI todos usando o mesmo Redis, ou migrar para ElastiCache sem
alterar o Compose da API.

5. Pergunta frequente
“Então o Redis está em outro processo, mas dentro da mesma VM/PC?”
Sim. Container = processo isolado com FS próprio, mas usa o mesmo kernel
do host. Para a aplicação isso parece “um servidor remoto” acessível por IP
privado.

TL;DR
Sempre foi um serviço separado; nunca uma thread Python.

No dev antigo, rodava como daemon do sistema → localhost.

Agora roda num container Redis → hostname redis dentro da rede Docker.

Código Python unchanged; apenas REDIS_URL aponta para o novo host.

---

[⬅️ Voltar para o início](../README.md)
