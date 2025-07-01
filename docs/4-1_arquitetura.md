# 🏗️ Arquitetura do Projeto Prisma

O **FastTrackAPI** utiliza uma arquitetura em camadas, cuidadosamente projetada para maximizar modularidade, escalabilidade, e manutenibilidade. Esta organização ajuda a separar claramente responsabilidades dentro da aplicação, facilitando testes, manutenção e expansão futura.

## 📂 Estrutura de Diretórios

O projeto está estruturado da seguinte forma:

```bash
fasttrackapi-projeto-prisma/
├── .github/
│   └── workflows/ 
│       └── ci.yml   
├── app/
│   ├── api/                      # Rotas da API (FastAPI Routers)
│   │   ├── v1/                   # Versão da API
│   │   │   ├── endpoints/        # Endpoints específicos (ex: user.py)
│   │   │   │   ├── auth.py       # 
│   │   │   │   ├── eventos.py    # 
│   │   │   │   ├── users.py      # 
│   │   │   │   └── ws_router.py  # Só conecta rotas com handlers
│   │   │   └── api_router.py     # Agrupa todos os endpoints da v1
│   ├── core/                     # Configurações globais da aplicação
│   │   ├── config.py             # Carrega variáveis de ambiente com Pydantic
│   │   ├── contextvars.py        # 
│   │   ├── logging_config.py     # Configuração estruturada de logs
│   │   └── security.py           # Configurações relacionadas à segurança/autenticação
│   ├── middleware/               # Middlewares customizados para logs e segurança
│   │   └── logging_middleware.py # 
│   ├── models/                   # Modelos do banco de dados (SQLAlchemy)
│   ├── repositories/             # Funções de acesso ao banco de dados (e fontes externas)?
│   │   ├── event_mem.py          # 
│   │   └── evento.py             # 
│   ├── schemas/                  # Modelos de entrada/saída (Pydantic)
│   │   ├── event_create.py       # 
│   │   ├── event_update.py       # 
│   │   ├── local_info.py         # 
│   │   ├── token.py              # 
│   │   ├── user.py               # 
│   │   ├── venue_type.py         # 
│   │   └── weather_forecast.py   # 
│   ├── services/                 # Regras de negócio e lógica de aplicação
│   │   ├── interfaces/           # 
│   │   │   ├── forecast_info.py  # 
│   │   │   ├── local_info.py     # 
│   │   │   └── user.py           # 
│   │   ├── auth_service.py       # 
│   │   ├── mock_forecast_info.py # 
│   │   ├── mock_local_info.py    # 
│   │   └── mock_users.py         # 
│   ├── utils/                    # Funções auxiliares, cache e decorators
│   │   └── cache.py              # 
│   ├── websockets/               # Comunicação em tempo real
│   │   ├── __init__.py           # 
│   │   ├── ws_manager.py         # Gerencia conexões
│   │   ├── ws_events.py          # Eventos relacionados a /eventos
│   │   └── ws_dashboard.py       # Contador ao vivo e usuários online
│   ├── deps.py                   # Gerenciador de dependências compartilhadas
│   └── main.py                   # Ponto de entrada da aplicação FastAPI
│
├── postgres-data/                # Aqui estão os dados do PostgreSQL
├── tests/                        # 
│   ├── unit/                     # Testes unitários
│   │   ├── __init__.py           # 
│   │   ├── conftest.py           # 
│   │   ├── test_auth.py          # 
│   │   ├── test_eventos.py       # 
│   │   ├── test_orecast_info.py  # 
│   │   └── test_local_info.py    # 
│   ├── integration/              # Testes de integração (rotas completas)
│   └── conftest.py               # Configurações e fixtures para testes
│
├── .env                          # Variáveis de ambiente (não versionado) ← padrão (dev)
├── .env.prod                     # ← produção
├── .env.test                     # ← testes/CI
├── docker-compose.yml            # Orquestração com banco de dados e Redis
├── Dockerfile                    # Imagem Docker da aplicação
├── pyproject.toml                # Gerenciado pelo Poetry (dependências, versão, etc)
├── poetry.lock                   # Trava das versões instaladas
├── README.md                     # Documentação principal do projeto
├── ROADMAP.md                    # 
├── TROUBLESHOOTING.md            # 
└── .gitignore                    # Arquivos ignorados pelo Git
```


## 🧱 Camadas da Aplicação

O FastTrackAPI é dividido nas seguintes camadas principais:

### 1. 📡 API (Routers)

* **Responsabilidade**: Recebe requisições HTTP, valida entradas, e delega ações para as camadas de serviço e repositório.
* **Tecnologia**: FastAPI
* **Exemplo**: `app/api/v1/endpoints/eventos.py`

### 2. 🎯 Serviços (Services)

* **Responsabilidade**: Implementam regras de negócio e lógica específica da aplicação.
* **Tecnologia**: Python puro, com protocolos para facilitar testes e substituições.
* **Exemplo**: `app/services/mock_local_info.py`

### 3. 📦 Repositórios (Repositories)

* **Responsabilidade**: Acessam e manipulam dados em banco de dados e APIs externas.
* **Tecnologia**: SQLAlchemy para PostgreSQL, protocolos abstratos, e repositórios em memória para testes.
* **Exemplo**: `app/repositories/event_mem.py`

### 4. 🗃️ Modelos e Schemas

* **Responsabilidade**: Definem estruturas de dados para comunicação entre camadas.
* **Tecnologia**: SQLAlchemy para modelos de banco e Pydantic para validações de entrada e saída.
* **Exemplo**: `app/schemas/event_create.py`

### 5. 🔐 Segurança e Autenticação

* **Responsabilidade**: Controle de acessos, autenticação JWT e gerenciamento de permissões.
* **Tecnologia**: OAuth2, JWT, passlib (bcrypt).
* **Exemplo**: `app/core/security.py`

### 6. 📈 Observabilidade e Logs

* **Responsabilidade**: Captura e registro estruturado de eventos e erros da aplicação.
* **Tecnologia**: structlog, middlewares personalizados.
* **Exemplo**: `app/core/logging_config.py`

### 7. 🚀 WebSockets e Comunicação em Tempo Real

* **Responsabilidade**: Suporte a funcionalidades real-time, como dashboards interativos e notificações.
* **Tecnologia**: WebSocket via FastAPI.
* **Exemplo**: `app/websockets/ws_manager.py`

## 🔄 Integração com Serviços Externos

O FastTrackAPI utiliza:

* **Banco de Dados Interno** (PostgreSQL com SQLAlchemy)
* **Banco Externo Simulado** (via API REST)
* **API Pública de Previsão do Tempo** (ex.: OpenWeatherMap)

Essas integrações demonstram uma aplicação realista e prática dos conceitos de arquitetura, segurança e comunicação com serviços externos.

---

## 🧱 Estrutura Conceitual dos Dados

### 1. Banco de Dados Interno (PostgreSQL)
Responsável por armazenar todos os dados principais dos eventos criados pelos usuários.

#### 📌 Informações Armazenadas no Evento:

| Campo          | Tipo        | Descrição                                                     |
|----------------|-------------|----------------------------------------------------------------|
| `id`           | int         | Identificador único do evento                                 |
| `title`        | str         | Título do evento                                              |
| `description`  | str         | Descrição detalhada                                           |
| `event_date`   | datetime    | Data e hora do evento                                         |
| `created_at`   | datetime    | Data de criação do evento                                     |
| `updated_at`   | datetime    | Última modificação                                            |
| `participants` | List[str]   | Lista de nomes dos participantes                              |
| `local_info`   | dict        | Dados retornados da API do banco externo (opcional)           |
| `forecast_info`| dict        | Dados retornados da API pública (opcional)                    |
| `views`        | int         | Quantidade de visualizações                                   |

PS.: `created_at` e `updated_at` ainda não estão implementadas no sistema.

---

### 2. Banco de Dados Externo Simulado (via API própria)
Esse "banco externo" será acessado via uma API REST e irá fornecer informações complementares sobre o local do evento.

#### 📡 Dados esperados da API externa:

| Campo          | Tipo        | Descrição                                                  |
|----------------|-------------|-------------------------------------------------------------|
| `location_name`| str         | Nome do local (chave de busca)                             |
| `capacity`     | int         | Capacidade máxima de pessoas                               |
| `venue_type`   | str         | Tipo de local (ex: auditório, salão, espaço aberto)        |
| `is_accessible`| bool        | Se possui acessibilidade                                   |
| `address`      | str         | Endereço completo                                          |

---

### 3. API Pública (OpenWeatherMap)
Servirá para buscar previsões meteorológicas para a data e local do evento.

#### 🌤️ Dados coletados:

| Campo             | Tipo     | Descrição                                 |
|------------------|----------|--------------------------------------------|
| `forecast_datetime` | datetime | Data e hora da previsão                  |
| `temperature`     | float    | Temperatura prevista (em °C)              |
| `weather_main`    | str      | Descrição curta (ex: Rain, Clear)         |
| `weather_desc`    | str      | Descrição completa (ex: light rain)       |
| `humidity`        | int      | Umidade relativa (%)                      |
| `wind_speed`      | float    | Velocidade do vento (m/s)                 |

### Sobre o uso de `Optional`
Em Python, `Optional[T]` significa que o campo pode ser do tipo `T` ou `None`.  
No Pydantic, isso permite que os campos sejam omitidos na entrada. Isso é útil para situações em que nem todos os dados estão disponíveis imediatamente, como é o caso de integrações com APIs externas que podem falhar ou demorar para responder.

---

## 📦 Tipos e Validações

Durante o desenvolvimento, os dados tratados incluem tipos comuns como texto (strings), números inteiros, valores decimais, datas e listas. Em alguns momentos, são utilizados tipos de dados estruturados mais flexíveis, como o tipo `dict`.

O tipo `dict` representa um conjunto de pares de chave e valor. Ele é útil quando o conteúdo pode variar ou não é conhecido com antecedência. Apesar disso, sempre que a estrutura de um dado for previsível, ela será modelada de forma explícita para garantir segurança e clareza no código.

Todos os dados manipulados nas entradas e saídas da aplicação serão validados por modelos `Pydantic`. O Pydantic permite criar classes que representam a estrutura esperada dos dados, garantindo que eles estejam no formato correto antes de serem usados ou armazenados. Ele também realiza conversões automáticas de tipo, fornece mensagens de erro claras em caso de dados inválidos e integra perfeitamente com o FastAPI para geração automática de documentação.

A utilização do Pydantic torna o projeto mais robusto, seguro e fácil de manter.

---

## 🧩 Schemas do Projeto

Os schemas representam os modelos de dados utilizados para entrada e saída de informações na API. Eles são criados com `Pydantic` e aproveitam o uso de `Annotated` para adicionar metadados como validações, descrições e regras de negócio.

### Modelos Criados:

- **EventCreate**: utilizado ao criar um novo evento. Permite inserir os dados principais, e os campos `local_info` e `forecast_info` são opcionais.
- **EventResponse**: utilizado quando for requisitado um evento do banco de dados, possui os campos de `id`, `forecast_info` e `views`.
- **EventUpdate**: utilizado para atualizar os dados de um evento após a criação. Exige os campos `local_info` e `forecast_info`, que contêm dados externos.
- **LocalInfo**: estrutura esperada da API simulada com dados sobre o local do evento, como capacidade, tipo, acessibilidade e endereço.
- **LocalInfoUpdate**: 
- **WeatherForecast**: estrutura que representa os dados retornados pela API pública de previsão do tempo.
- **ForecastInfoUpdate**: 
- **Token**: 
- **User**:
- **UserinDB**: 
- **VenueTypes**:

Todos esses modelos estão localizados na pasta `app/schemas/` e são essenciais para garantir a validação de dados, a integridade da aplicação e a geração automática da documentação da API via OpenAPI/Swagger.

---

[⬅️ Voltar para o início](../README.md)
