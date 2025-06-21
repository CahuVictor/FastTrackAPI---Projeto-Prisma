# FastTrackAPI – Projeto Prisma

[![Coverage](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma)
---------- coverage: platform win32, python 3.12.6-final-0 -----------
Name                                                Stmts   Miss  Cover   Missing
TOTAL                                                 863    107    88%

Required test coverage of 80% reached. Total coverage: 82.36%

Este repositório faz parte de uma mentoria prática de backend com Python e FastAPI.  
O **Projeto Prisma** representa a construção de uma base sólida e estruturada, refletindo a clareza e a organização de um backend bem projetado.

A proposta do **FastTrackAPI** é acelerar o aprendizado, explorando na prática os principais pilares do desenvolvimento backend moderno:

- Arquitetura de Software
- Boas Práticas de Código
- Segurança (JWT, OAuth2, controle de acesso)
- Versionamento com Git e GitHub
- Testes Automatizados com Pytest
- DevOps com Docker, Docker Compose e GitHub Actions
- Observabilidade (Logging e Monitoramento)
- Integração com Banco de Dados via SQLAlchemy + Alembic
- Cache com Redis e Background Tasks
- Documentação e Deploy

O projeto é modular, versionado publicamente e busca simular um ambiente profissional, servindo como referência para estudos e futuros sistemas reais.

---

## 🎯 Objetivo Geral

Desenvolver habilidades avançadas em desenvolvimento backend com Python utilizando o framework FastAPI, compreendendo arquitetura de software, segurança, práticas modernas de DevOps, testes automatizados, observabilidade e documentação, por meio da construção de um projeto prático hospedado no GitHub.

---

## 📌 Objetivos Específicos Detalhados

- [ ] **Dominar os fundamentos e recursos avançados do FastAPI**
  - [x] Criar rotas RESTful com métodos GET, POST, PUT, DELETE
  - [x] Utilizar `Depends` para injeção de dependências
  - [x] Validar dados de entrada e saída com Pydantic
  - [x] Utilizar tags, responses e exemplos para a documentação automática
  - [ ] Implementar Background Tasks
  - [x] Trabalhar com WebSockets
  - [x] Fazer upload e download de arquivos

- [ ] **Aplicar arquitetura de software adequada para aplicações backend**
  - [x] Organizar a aplicação em camadas (router, service, repository, schema, model)
  - [ ] Aplicar princípios SOLID, DRY, KISS e YAGNI
  - [x] Criar dependências reutilizáveis e testáveis
  - [ ] Adotar um padrão de projeto para escalar o backend

- [ ] **Implementar boas práticas de segurança no backend**
  - [x] Utilizar autenticação com JWT
  - [x] Implementar autorização com escopos e permissões
  - [x] Proteger rotas com `Depends` e lógica de verificação
  - [x] Armazenar senhas com hash seguro (bcrypt, passlib)
  - [ ] Prevenir vulnerabilidades comuns (SQL Injection, XSS, etc)

- [ ] **Utilizar ferramentas e práticas de DevOps no fluxo de desenvolvimento**
  - [x] Utilizar Docker para empacotar a aplicação
  - [x] Orquestrar serviços com Docker Compose (app, banco, redis)
  - [x] Criar pipelines de CI com GitHub Actions (teste e lint automático)
  - [ ] Rodar migrations de banco em containers (ex: Alembic via Compose)

- [x] **Gerenciar configurações de forma segura e flexível**
  - [x] Utilizar `.env` com Pydantic Settings
  - [x] Separar configurações por ambiente (dev, prod, test)
  - [x] Garantir fallback seguro para variáveis obrigatórias

- [x] **Desenvolver testes automatizados**
  - [x] Criar testes unitários com `pytest`
  - [x] Implementar testes de integração simulando requisições reais
  - [x] Utilizar mocks para isolar dependências em testes
  - [x] Medir cobertura de código com `pytest-cov`

- [ ] **Adicionar observabilidade e monitoramento à aplicação**
  - [x] Adicionar logs estruturados com `loguru` ou `structlog`
  - [x] Criar middlewares para registrar requisições/respostas
  - [ ] Monitorar erros e alertas (integração futura com ferramentas externas)

- [x] **Documentar a API e o projeto de forma clara e profissional**
  - [x] Aproveitar documentação automática do Swagger/OpenAPI
  - [x] Adicionar exemplos e descrições nos modelos Pydantic
  - [x] Manter um `README.md` atualizado e bem estruturado

- [ ] **Aprofundar o uso de banco de dados com SQLAlchemy**
  - [x] Criar modelos ORM com relacionamentos
  - [ ] Escrever queries mais avançadas (joins, agregações)
  - [x] Implementar filtros e paginação em endpoints
  - [x] Gerenciar migrações com Alembic

- [x] **Trabalhar com versionamento de código no GitHub com boas práticas**
  - [x] Utilizar branches e pull requests para organizar o fluxo de trabalho
  - [x] Escrever mensagens de commit claras e informativas
  - [x] Resolver conflitos de merge com segurança

- [ ] **Explorar funcionalidades avançadas conforme a evolução do projeto**
  - [x] Usar cache com Redis para otimização de desempenho
  - [ ] Realizar deploy em nuvem (Render, Railway ou VPS)
  - [ ] Testar uso de workers com Celery ou RQ (tarefa opcional)
  - [ ] Expor métricas básicas (ex: Prometheus ou logs customizados)

---

## 🗂️ Estrutura de Pastas

```bash
fasttrackapi-projeto-prisma/
├── .github/
│   └── workflows/ 
│       └── ci.yml   
├── app/
│   ├── api/                    # Rotas da API (FastAPI Routers)
│   │   ├── v1/                 # Versão da API
│   │   │   ├── endpoints/      # Endpoints específicos (ex: user.py)
│   │   │   │   ├── auth.py     # 
│   │   │   │   ├── eventos.py  # 
│   │   │   │   ├── users.py    # 
│   │   │   │   └── ws_router.py            # Só conecta rotas com handlers
│   │   │   └── api_router.py   # Agrupa todos os endpoints da v1
│   ├── core/                   # Configurações globais da aplicação
│   │   ├── config.py           # Carrega variáveis de ambiente com Pydantic
│   │   ├── contextvars.py      # 
│   │   ├── logging_config.py   # 
│   │   └── security.py         # Configurações relacionadas à segurança/autenticação
│   ├── middleware/             # 
│   │   └── logging_middleware.py # 
│   ├── models/                 # Modelos do banco de dados (SQLAlchemy)
│   ├── repositories/           # Funções de acesso ao banco de dados
│   │   ├── event_mem.py       # 
│   │   └── evento.py           # 
│   ├── schemas/                # Modelos de entrada/saída (Pydantic)
│   │   ├── event_create.py     # 
│   │   ├── event_update.py     # 
│   │   ├── local_info.py       # 
│   │   ├── token.py            # 
│   │   ├── user.py             # 
│   │   ├── venue_type.py       # 
│   │   └── weather_forecast.py # 
│   ├── services/               # Lógica de negócio
│   │   ├── interfaces/                 # 
│   │   │   ├── forecast_info.py             # 
│   │   │   ├── local_info.py       # 
│   │   │   └── user.py # 
│   │   ├── auth_service.py            # 
│   │   ├── mock_forecast_info.py             # 
│   │   ├── mock_local_info.py       # 
│   │   └── mock_users.py # 
│   ├── utils/                  # Funções auxiliares
│   │   └── cache.py # 
│   ├── deps.py                 # Dependências compartilhadas (ex: get_db)
│   └── main.py                 # Ponto de entrada da aplicação FastAPI
│
├── tests/
│   ├── unit/                   # Testes unitários
│   │   ├── __init__.py            # 
│   │   ├── conftest.py              # 
│   │   ├── test_auth.py       # 
│   │   ├── test_eventos.py              # 
│   │   ├── test_orecast_info.py       # 
│   │   └── test_local_info.py # 
│   ├── integration/            # Testes de integração (rotas completas)
│   └── conftest.py             # Configurações e fixtures para testes
├── websockets/
│   ├── __init__.py
│   ├── manager.py              # Gerencia conexões
│   ├── events.py               # Eventos relacionados a /eventos
│   └── dashboard.py            # Contador ao vivo e usuários online
│
├── .env                        # Variáveis de ambiente (não versionado) ← padrão (dev)
├── .env.prod                   # ← produção
├── .env.test                   # ← testes/CI
├── docker-compose.yml          # Orquestração com banco de dados e Redis
├── Dockerfile                  # Imagem Docker da aplicação
├── pyproject.toml              # Gerenciado pelo Poetry (dependências, versão, etc)
├── poetry.lock                 # Trava das versões instaladas
├── README.md                   # Documentação principal do projeto
├── ROADMAP.md                  # 
├── TROUBLESHOOTING.md          # 
└── .gitignore                  # Arquivos ignorados pelo Git
```

---

## 🧪 Finalidade do Projeto

O Projeto Prisma simula uma aplicação real de gerenciamento de eventos, proporcionando a integração com múltiplas fontes de dados e promovendo uma experiência prática de desenvolvimento backend completo.

### Visão Geral

A aplicação permite que usuários criem e visualizem eventos. Cada evento pode conter informações como título, descrição, data e local. Além disso, a aplicação enriquece os dados do evento com informações obtidas de fontes externas:

1. **Banco de Dados Interno (PostgreSQL):**  
   Armazena todas as informações principais dos eventos, como título, descrição, data, local e participantes.

2. **Banco de Dados Externo Simulado (API controlada):**  
   Representa um sistema externo com dados complementares, como a capacidade de locais ou histórico de eventos em determinado espaço. Esse banco será acessado via uma API REST criada especificamente para simular esse comportamento.

3. **API Pública (OpenWeatherMap):**  
   Fornece previsões do tempo baseadas na data e local do evento, integrando dados do mundo real à aplicação.

### Exemplo de Fluxo

- O usuário cria um evento pelo backend.
- A aplicação:
  - Armazena os dados no banco de dados interno.
  - Consulta a API simulada para informações do local.
  - Consulta a API pública para obter a previsão do tempo.
- Os dados combinados são exibidos ao usuário final.

### Benefícios Técnicos

- Simula um ambiente profissional com múltiplas fontes de dados.
- Exerce o consumo de APIs externas com autenticação.
- Trabalha com integração de banco de dados interno e APIs REST externas.
- Promove a aplicação dos conceitos de arquitetura, segurança, testes e boas práticas.

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

## 🧭 Próximo Passo do Desenvolvimento

O próximo passo será **escolher uma das três frentes iniciais para iniciar o desenvolvimento prático**:

1. **Criar a primeira rota da API (ex: rota de usuários ou status)**  
2. **Configurar o banco de dados e a primeira modelagem com SQLAlchemy + Alembic**  
3. **Implementar os primeiros testes automatizados com Pytest**

> Recomendação: começar pela criação da primeira rota para já ver a API funcionando e integrar gradualmente os demais pontos.

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
| `location_name`| str         | Nome do local (referência cruzada com API externa)            |
| `created_at`   | datetime    | Data de criação do evento                                     |
| `updated_at`   | datetime    | Última modificação                                            |
| `participants` | List[str]   | Lista de nomes dos participantes                              |
| `local_info`   | dict        | Dados retornados da API do banco externo (opcional)           |
| `forecast_info`| dict        | Dados retornados da API pública (opcional)                   |

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
| `past_events`  | List[str]   | Lista de eventos anteriores já realizados nesse local      |

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
- **EventUpdate**: utilizado para atualizar os dados de um evento após a criação. Exige os campos `local_info` e `forecast_info`, que contêm dados externos.
- **LocalInfo**: estrutura esperada da API simulada com dados sobre o local do evento, como capacidade, tipo, acessibilidade e endereço.
- **WeatherForecast**: estrutura que representa os dados retornados pela API pública de previsão do tempo.

Todos esses modelos estão localizados na pasta `app/schemas/` e são essenciais para garantir a validação de dados, a integridade da aplicação e a geração automática da documentação da API via OpenAPI/Swagger.

---

## 🔧 Modificações recentes

- Migração da estrutura de armazenamento de lista para `dict` (`eventos_db`)
- Uso de tipos explícitos de retorno nas funções de endpoint
- `location_name` removido da entrada direta do usuário (`EventCreate`)
- `LocalInfo` é gerado com base em API externa; se não houver retorno, salva-se apenas `location_name`

---

## 🤪 Como executar localmente

### Pré-requisitos
- Python 3.12+
- [Poetry](https://python-poetry.org/docs/)

### Instalação e execução

```bash
# Clone o repositório
https://github.com/seu-usuario/FastTrackAPI---Projeto-Prisma.git
cd FastTrackAPI---Projeto-Prisma

# Instale as dependências
poetry install

# (opcional) Ative o shell do poetry
poetry self add poetry-plugin-shell  # somente na primeira vez
poetry shell

# Execute a aplicação
uvicorn app.main:app --reload
```

projetos FastAPI.

✅ Passo a passo para testar localmente
1. 📦 Ative o ambiente virtual (ou use o poetry se estiver configurado)
Se estiver usando venv:

poetry install

Habilitar o plugin de shell antigo
Se você quiser voltar a usar o poetry shell, rode isso uma única vez:

poetry self add poetry-plugin-shell

Depois você poderá usar normalmente:

poetry shell

2. 📥 Instale o FastAPI e o Uvicorn (se ainda não tiver)


pip install fastapi uvicorn

3. ▶️ Execute o servidor
A partir da pasta raiz do projeto (onde está o diretório app/), rode:

uvicorn app.main:app --reload

Isso diz: “inicie a aplicação FastAPI localizada em app/main.py, dentro do objeto app”

4. 🌐 Acesse a documentação da API

Após rodar o comando, acesse:

http://localhost:8000/docs → Swagger UI (interativo)

http://localhost:8000/redoc → ReDoc (documentação formal)

Você pode instalar a lib diretamente com o Poetry   como uma dependência de desenvolvimento (ideal para testes). Ex com o httpx

poetry add --dev httpx

### Acesse a API
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Testes

```bash
# Execute todos os testes com cobertura
pytest --cov=app --cov-report=term-missing
poetry run pytest --cov=app --cov-report=xml --cov-report=html
```

Para garantir que tudo funcione corretamente, instale as dependências de teste:

```bash
poetry add --dev pytest pytest-cov httpx
```

### Sobre o pyproject.toml

- As dependências principais ficam na seção `[tool.poetry.dependencies]`
- As dependências de desenvolvimento (testes, lint, etc.) vão em `[tool.poetry.group.dev.dependencies]`

Exemplo:
```toml
[tool.poetry.dependencies]
fastapi = "^0.110.0"
uvicorn = "^0.29.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^4.1.0"
httpx = "^0.27.0"
```

---

### CI com GitHub Actions

O projeto pode utilizar GitHub Actions para rodar testes automaticamente a cada push ou pull request.

Crie um arquivo `.github/workflows/tests.yml` com o conteúdo:

```yaml
name: Testes e Cobertura

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout do repositório
        uses: actions/checkout@v3

      - name: Instalar Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Instalar Poetry
        run: |
          pip install poetry
          poetry install

      - name: Rodar testes com cobertura
        run: |
          poetry run pytest --cov=app --cov-report=xml --cov-report=term

      - name: Enviar para Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

Certifique-se de criar uma conta no [https://codecov.io](https://codecov.io) e conectar com seu repositório GitHub para ativar o badge corretamente.

Rodar testes localmente igual ao CI
# 1ª vez
  poetry install --with dev --no-interaction
# sempre que for commitar
  poetry run pytest --cov=app --cov-report=term-missing

Adicione a dependência no grupo dev para rodar localmente:
  poetry add --group dev ruff

# pyproject.toml
[tool.ruff]
line-length = 100               # segue no nível raiz (formatação)

[tool.ruff.lint]                # ⬅️ tudo abaixo diz respeito ao *linter*
select = ["E", "F", "I", "UP", "D"]   # incluí "D" para docstrings
ignore = ["F401"]                     # exemplo: allow unused import
extend-ignore = ["D203", "D213"]      # (explico no ponto 2)
preview = true                        # já usa as regras “next-gen”

# Regras diferentes para testes
[tool.ruff.per-file-ignores]
"tests/**/*" = ["D", "E501"]         # sem docstring + sem limite de linha

# Exemplo de exclusão de diretório
[tool.ruff.exclude]
extend = ["migrations", "scripts"]

2 ⚠️ Conflito D203 × D211 e D212 × D213
Esses são regras de docstring da família pydocstyle:

Código	Regra resumida	Incompatível com
D203	“Precisa de uma linha em branco antes de cada class docstring”	D211
D211	“Não pode haver linha em branco antes da docstring”	D203
D212	Para docstring multilinha, o resumo deve iniciar na primeira linha	D213
D213	Para docstring multilinha, o resumo deve iniciar na segunda linha	D212

Rode Ruff + Pytest com os mesmos flags:
  poetry run ruff check .
  pyupgrade --py312-plus --exit-zero-even-if-changed $(git ls-files '*.py')
  poetry run mypy app
  poetry run bandit -q -r app -lll
  poetry run pytest -x --cov=app --cov-report=xml --cov-report=html --cov-fail-under=80
    poetry run pytest tests/unit/test_localinfo.py --cov=app --cov-fail-under=80
    poetry run pytest --cov=app --cov-report=xml --cov-report=html --cov-fail-under=80

Seguindo esses passos, você terá um pipeline que:
  Corrige estilo e ordena imports (Ruff)
  Alerta para sintaxe obsoleta (PyUpgrade)
  Garante tipagem correta (MyPy)
  Aponta falhas de segurança (Bandit)
  Executa testes com cobertura mínima definida

Se você quiser simular o workflow localmente, use o act (opcional):
  brew install act            # ou choco install act no Windows
  act push --job test

Anotações no PR: quando um action devolve logs no formato GitHub Diagnostic Format, o GitHub cria inline comments na aba Files changed.
  ruff check --output-format=github

Erros “fixáveis” (marcados com [*]):
  poetry run ruff check --fix .

Erros não auto-corrigíveis:

F821 timezone → faltou importar ou definir timezone.

F811 redefinition → tem duas funções/fixtures com o mesmo nome; renomeie ou remova duplicata.

F601 key 201 repeated → você tem {201: ..., 201: ...} na mesma dict.

Undefined name EventCreate nos testes → adicione from app.schemas.event_create import EventCreate.

.

1️⃣ MyPy – verificador de type hints
  ✨ O que é
  Analisa os type hints do Python (def foo(x: int) -> str:) e compara com o fluxo real do código.

  Encontra incongruências de tipos antes de você rodar o programa.

  ⚙️ Como adicionar
    poetry add --group dev mypy

.

2️⃣ Bandit – linter de segurança
  ✨ O que é
  Avalia source Python em busca de “Common Weaknesses” (CWE):
  ‣ uso de eval, ‣ chaves criptográficas hard-coded, ‣ subprocess sem shell=False, ‣ hashlib.md5, etc.

  ⚙️ Como adicionar
    poetry add --group dev bandit

.

3️⃣ PyUpgrade – modernizador de sintaxe
  ✨ O que é
  Reescreve automaticamente trechos antigos para a versão Python que você escolher. Exemplos:

  list(x for x in y) → [x for x in y]

  from typing import List + List[int] → list[int] (Py 3.9+)

  Remove six, converte super(Class, self) → super()

  ⚙️ Como adicionar
    poetry add --group dev pyupgrade
  Uso local
    pyupgrade --py312-plus $(git ls-files '*.py')

CodeQL e DependaBoot onhold por enquanto
4️⃣ CodeQL – análise de vulnerabilidade mantida pelo GitHub
✨ O que é
Compila seu projeto para um grafo semântico e executa consultas (“queries”) que detectam padrões inseguros, SQL-Injection, Path-Traversal etc.
É a solução oficial de Code Scanning do GitHub Advanced Security (grátis em repositórios públicos).

5️⃣ Dependabot (Security Spotlight)
✨ O que é
Serviço do GitHub que cria Pull Requests automáticos quando sai versão nova (ou patch de segurança) de dependências.


---

## Links de Referência

https://open-meteo.com/en/docs
https://open-meteo.com/en/docs?latitude=-8.0539&longitude=-34.8811
https://publicapis.dev/
https://www.mongodb.com/try/download/odbc-driver


Pendente organização

FastTrackAPI – Projeto Prisma 🚀

Projeto-laboratório de mentoria em backend Python/FastAPI. Aqui testamos, na prática, arquitetura limpa, segurança, DevOps, testes e observabilidade — tudo versionado no GitHub.

📚 Sumário

Visão Geral

Objetivos

Estrutura de Pastas

Configuração por Ambiente + Fallback Seguro

Dependências Reutilizáveis e Testáveis

Filtros & Paginação in-memory

Cache com Redis

Pipeline CI (GitHub Actions)

Roadmap de Evolução

Como Executar Localmente

Visão Geral

O FastTrackAPI simula um sistema que gerencia eventos. Ele reúne diferentes tecnologias como banco de dados (PostgreSQL), APIs externas para previsão do tempo e informações locais, oferecendo uma experiência prática completa em backend Python com FastAPI.

Objetivos

Geral

Capacitar no desenvolvimento backend usando Python e FastAPI, com práticas modernas em segurança, testes automatizados e DevOps.

Específicos

Implementar uma arquitetura em camadas com boas práticas (SOLID, DRY, KISS).

Usar testes automatizados para garantir a qualidade.

Realizar integração contínua e deploy contínuo (CI/CD).

Utilizar cache para otimizar desempenho.

Estrutura de Pastas

fasttrackapi-projeto-prisma/
├── app/
│   ├── api/v1/endpoints/   # Rotas (URLs) da aplicação.
│   ├── core/               # Configurações centrais (ambientes, segurança).
│   ├── repositories/       # Interfaces e implementações para acessar os dados.
│   ├── services/           # Regras de negócio e mocks para testes.
│   ├── schemas/            # Modelos dos dados usados na aplicação.
│   ├── utils/              # Funções úteis e ferramentas (cache, etc.).
│   └── deps.py             # Gerencia dependências da aplicação.
├── tests/                  # Testes automatizados.
├── Dockerfile              # Arquivo para criação de container Docker.
├── docker-compose.yml      # Gerenciamento de múltiplos containers.
├── .env                    # Variáveis de ambiente.
└── .github/workflows/ci.yml # Configuração do pipeline de integração contínua.

Configuração por Ambiente + Fallback Seguro

O sistema suporta três ambientes: desenvolvimento (dev), testes (test) e produção (prod). Cada um possui seu próprio arquivo .env, que é carregado automaticamente pelo sistema. Caso faltem variáveis obrigatórias em produção, o sistema gera um alerta, garantindo segurança e estabilidade.

Dependências Reutilizáveis e Testáveis

As dependências são organizadas em protocolos (contratos) definidos claramente. Isso permite facilmente substituir implementações reais por versões simplificadas (mocks) durante os testes, garantindo testes rápidos, claros e independentes.

Filtros & Paginação in-memory

Antes de conectar o banco de dados definitivo, usamos um método interno para realizar filtros e paginação diretamente na memória do sistema. Isso permite que as APIs sejam testadas rapidamente sem depender do banco externo.

Cache com Redis

Usamos o Redis para armazenar temporariamente resultados de operações comuns e demoradas, reduzindo a carga no sistema e melhorando a performance geral da aplicação. Exemplos são resultados de previsões climáticas e informações locais que raramente mudam.

Pipeline CI (GitHub Actions)

A integração contínua (CI) é configurada através do GitHub Actions, que realiza automaticamente os seguintes passos ao atualizar o código:

Executa testes em diferentes versões do Python (3.10, 3.11, 3.12) em múltiplas plataformas (Ubuntu e Windows).

Analisa o código buscando erros de estilo e segurança.

Verifica cobertura de testes.

Publica relatórios de testes e cobertura automaticamente.

Roadmap de Evolução

Planejamento futuro detalhado:

Implementação de logs estruturados.

Automatização de tarefas em segundo plano.

Melhorias de segurança (controle de acessos, proteção contra ataques).

Implantação da aplicação em ambiente de produção real usando containerização.

Como Executar Localmente

Passo a passo simples

Clone o projeto:

git clone https://github.com/SEU_USUARIO/FastTrackAPI---Projeto-Prisma.git
cd FastTrackAPI---Projeto-Prisma

Instale as dependências:

poetry install

Inicie o servidor local em ambiente de desenvolvimento:

uvicorn app.main:app --reload

Acesse a documentação interativa:

http://localhost:8000/docs

Execução de testes:

ENV=test pytest -q

Com estas instruções detalhadas, você já pode começar a trabalhar no FastTrackAPI – Projeto Prisma, praticando desenvolvimento backend com qualidade profissional!

# FastTrackAPI – Projeto Prisma

[![Coverage](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma)

---

## ✅ Atualização: Dependências Reutilizáveis e Testáveis

Este projeto adota o padrão de **injeção de dependência com contratos (Protocol)** para tornar o código mais **modular**, **testável** e **substituível** sem alterar os endpoints principais.

### 📌 O que foi feito:

1. **Definimos contratos (`Protocol`)** para todos os serviços: usuários, eventos, previsão do tempo e local.
2. **Criamos implementações mockáveis** com dados estáticos para testes e desenvolvimento.
3. **Registramos providers únicos** no arquivo `deps.py`, permitindo troca fácil entre mocks e implementações reais.
4. **Atualizamos todos os endpoints** para receberem dependências via `Depends(...)`, sem acoplamento a implementações concretas.

### 🔍 Benefícios desta abordagem

* **Testes unitários e de integração facilitados:** cada serviço pode ser substituído por um fake/mocker no momento do teste, sem alterar a lógica das rotas.
* **Menor acoplamento:** a lógica da aplicação depende apenas de contratos, não de implementações específicas.
* **Flexibilidade futura:** mudar de banco de dados ou de API de clima exige apenas trocar a implementação do contrato, mantendo as rotas intactas.
* **Alinhado ao SOLID (Dependency Inversion Principle):** alta coesão, baixo acoplamento e extensibilidade segura.

### 🧪 O que pode ser testado com essa estrutura

Com o uso de dependências injetáveis, é possível testar isoladamente:

* Autenticação de usuários (via `MockUserRepo`)
* Consultas e atualizações de eventos (via `InMemoryEventoRepo`)
* Enriquecimento de eventos com previsão do tempo (`MockForecastService`)
* Enriquecimento de eventos com dados de local (`MockLocalInfoService`)
* Respostas esperadas para permissões e acessos (admin, editor, viewer)

### 🧩 Exemplo de contrato criado:

```python
# app/repositories/evento.py
from typing import Protocol
from app.schemas.event_create import EventCreate, EventResponse

class AbstractEventRepo(Protocol):
    def list_all(self) -> list[EventResponse]: ...
    def get(self, evento_id: int) -> EventResponse | None: ...
    def add(self, evento: EventCreate) -> EventResponse: ...
    def replace_all(self, eventos: list[EventResponse]) -> list[EventResponse]: ...
    def replace_by_id(self, evento_id: int, evento: EventResponse) -> EventResponse: ...
    def delete_all(self) -> None: ...
    def delete_by_id(self, evento_id: int) -> bool: ...
    def update(self, evento_id: int, data: dict) -> EventResponse: ...
```

---

> 💡 Todos os serviços que dependem de `users`, `forecast`, `local_info` e `eventos` já foram refatorados. Veja exemplos no diretório `app/services/`, `app/repositories/` e `app/deps.py`.

# FastTrackAPI – Projeto Prisma

[![Coverage](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma)

Este repositório faz parte de uma mentoria prática de backend com Python e FastAPI.

---

## 🔐 Configuração por Ambiente + Fallback Seguro

Gerenciamos **três ambientes padrão** — `dev`, `test` e `prod` — cada qual com seu próprio arquivo de variáveis:

| Arquivo     | Quando é lido                   | Exemplo de conteúdo                                             |
| ----------- | ------------------------------- | --------------------------------------------------------------- |
| `.env`      | Desenvolvimento local (default) | `ENVIRONMENT=dev`    `DB_URL=postgres://localhost/dev_db`       |
| `.env.test` | Execução da suíte *pytest*/CI   | `ENVIRONMENT=test`    `DB_URL=postgres://localhost/test_db`     |
| `.env.prod` | Deploy em produção              | `ENVIRONMENT=prod`    `DB_URL=postgres://postgres:5432/prod_db` |

> **Importante:** nunca commitamos segredos reais em `.env.prod`. Em produção as chaves vêm de *secret‑manager* ou de variáveis do host.

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

✍️ Proposta de adição ao README.md
markdown
Copiar
## Filtros e Paginação *in-memory*

> **Por que existe:** antes de ligar um banco SQL/NoSQL queremos que a API já exponha paginação (`skip` / `limit`) e filtros de consulta (ex.: `city=Recife`). Assim o front-end e os testes de integração continuam exatamente iguais quando trocarmos a camada de persistência — princípio **OCP / port-adapter**.

### Como funciona

1. **Repositório em memória**  
   `app/repositories/event_mem.py` ganhou o método  
   ```python
   def list_partial(self, *, skip: int = 0, limit: int = 20, **filters)
Constrói uma lista a partir do dicionário interno

Aplica cada filtro recebido (city, date_from, etc.)

Devolve apenas a fatia data[skip: skip+limit]

Contrato da interface
A AbstractEventRepo ( app/repositories/evento.py ) agora declara list_partial, garantindo que qualquer implementação futura (SQLAlchemy, Elastic, Redis…) respeite a mesma assinatura.

Rotas

GET /api/v1/eventos
Recebe skip, limit, city como query params e simplesmente delega para repo.list_partial(...)

A rota legada /eventos/todos foi removida: listar tudo sem filtro/paginação não é mais suportado.

Testes

tests/unit/test_eventos.py atualizados para fabricar eventos via Pydantic (EventCreate) e cobrir cenários de paginação e filtros.

Cobertura total da suíte volta a ficar ≥ 80 %.

Benefícios imediatos
✔️ Benefício	🚀 Impacto
Mesmo contrato HTTP hoje e depois do banco	zero retrabalho no front-end
Feedback rápido no CI – tudo roda só em RAM	build & testes ≤ 5 s
Facilita benchmark de slice vs cursor	decide-se depois se precisa de paginação baseada em cursor ou token
Permite cachê fácil na etapa seguinte	a lista paginada já é determinística → @cache

Próximos passos possíveis
Trocar storage: basta criar EventoSQLRepo que implemente list_partial com select(...).where(...).offset(skip).limit(limit).

Novos filtros: adicione parâmetros opcionais na rota e passe-os ao repo; a assinatura pública permanece idêntica.

Cursor Pagination: manter skip/limit para retro-compatibilidade e aceitar um cursor para coleções muito grandes.

💡 Onde olhar no código

Arquivo	O que mudou
app/repositories/evento.py	nova list_partial na interface
app/repositories/event_mem.py	implementação da função + refactor interno
app/api/v1/endpoints/eventos.py	rota /eventos usa list_partial; rota /eventos/todos removida
tests/unit/test_eventos.py	usa modelos Pydantic e cobre paginação/filtros

Copie o bloco acima para o seu README.md (ou crave um link direto para este ponto do documento se já existir uma seção “Arquitetura”). Qualquer ajuste de nomenclatura/caminho é só trocar aqui e dar git commit -m "docs(readme): explica filtros e paginação in-memory".






🔄 Atualização sugerida para o README.md
markdown
Copiar
Editar
## Filtros e Paginação *in-memory*

> **Motivação:** antes de plugarmos PostgreSQL/SQLAlchemy, já queremos que a API exponha paginação (`skip` + `limit`) e filtros arbitrários via *query params*. Assim o front-end, os testes e a documentação Swagger permanecem **iguais** quando trocarmos apenas a camada de persistência — princípio Open-Closed (OCP).

---

### Visão de alto nível  

1. **Repositório em memória**  
   `app/repositories/event_mem.py` implementa  
   ```python
   def list_partial(self, *, skip: int = 0, limit: int = 20, **filters)
Converte o dicionário interno em lista.

Aplica dinamicamente cada par chave=valor recebido (ex.: city="Recife").

Retorna somente a fatia data[skip : skip + limit].

📝 Por que **filters?

Evita “quebrar” o contrato público quando surgirem filtros novos (ex.: date_from, venue_type).

As implementações futuras (SQL ou Elastic) continuam obedecendo à mesma assinatura, trocando apenas o corpo da função.

Contrato da interface
app/repositories/evento.py declara o mesmo método genérico:

python
Copiar
Editar
def list_partial(self, *, skip: int = 0, limit: int = 20, **filters) -> list[EventResponse]: ...
Rotas

GET /api/v1/eventos

python
Copiar
Editar
eventos = repo.list_partial(skip=skip, limit=limit, city=city)
— qualquer filtro é simplesmente encaminhado como keyword arg.

GET /api/v1/eventos/todos
Mantida apenas para retro-compatibilidade:

python
Copiar
Editar
@router.get("/eventos/todos", deprecated=True, include_in_schema=False)
Ela chama repo.list_all() e logo será removida.

Testes

tests/unit/test_eventos.py fabrica objetos via Pydantic (EventCreate) e cobre cenários de paginação e filtros.

Cobertura total ≥ 80 %.

Onde está cada parte
Arquivo	Conteúdo relevante
app/repositories/evento.py	interface AbstractEventRepo com list_partial(**filters)
app/repositories/event_mem.py	primeiro adapter concreto: filtra e pagina em RAM
app/api/v1/endpoints/eventos.py	rota /eventos usa o repo; rota /eventos/todos marcada deprecated=True
tests/unit/test_eventos.py	cenários de paginação e filtros com objetos Pydantic

Benefícios imediatos
✔️	Impacto
Contrato estável com **filters	adicionar novos filtros não muda assinatura nem quebra clientes
Feedback ultra-rápido	CI roda tudo em memória; sem container de banco
Migração suave	trocar por session.exec(stmt.where(...).offset(skip).limit(limit)) e pronto
Base p/ cache ou cursor pagination	slice determinístico facilita evoluções de performance

Próximos passos
Adicionar filtros extras: basta incluir o parâmetro na rota e encaminhar para list_partial.

Trocar storage: crie SQLEventoRepo que obedece à mesma assinatura.

Cursor-based pagination: manter skip/limit para retro-compatibilidade e aceitar cursor opcional.

sql
Copiar
Editar

Copie o bloco acima para o `README.md` (em “Arquitetura” ou “Features”) e faça o commit:

```bash
git add README.md
git commit -m "docs(readme): descreve filtros e paginação in-memory com **filters"
Assim o repositório continua documentado em sintonia com a implementação real.



**filters percorrido dinamicamente	Escalável: novos filtros (ex. date_from) não exigem refactor de assinatura nem de testes.
Comparação “case-insensitive” só para str	Evita falso-negativo em campos textuais sem afetar tipos numéricos/datas.
expected is None → filtro é ignorado	Permite passar o parâmetro sempre, sem precisar de condicionais na rota (`city: str
Docstring com exemplos	Facilita entendimento para quem implementar o próximo adapter (SQL, Elastic etc.).

— e, quando você quiser acrescentar outro parâmetro (date_from, venue_type…), basta incluí-lo no Query(...) da rota e repassar para list_partial sem alterar o contrato nem quebrar clientes.

## 4. Cache com Redis para Desempenho 

>  Esta seção explica *por quê* e *como* o Projeto Prisma usa o Redis como cache de respostas. Ela complementa o passo‑a‑passo detalhado já descrito no Roadmap.

### 4.1 Visão geral 

|                                |  Sem cache                                                  |  Com Redis (cache‑aside)                                                                                                |
| ------------------------------ | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Fluxo de requisição            | FastAPI → Service → API externa ou consulta lenta → Cliente | FastAPI → **Redis GET** → *HIT*? ✔ devolve em ◉ ms / *MISS* ✖ → Service → API externa → **Redis SETEX** (TTL) → Cliente |
| Latência média                 |  100–800 ms                                                 |  ≈1–5 ms após o primeiro acesso                                                                                         |
| Carga no backend/API terceiros | 100 % das requisições                                       | 1 requisição a cada *TTL*                                                                                               |

**Estratégia:** usamos o padrão *cache‑aside* (comumente chamado read‑through): a própria aplicação consulta o cache antes de executar a operação cara e grava o resultado quando não encontra a chave.

---

### 4.2 Abordagem adotada no código

|  Camada                |  Arquivo / Elemento                                                                                                     |  Descrição                                                                                              |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Provider**           | `app/deps.py → provide_redis()`                                                                                         | Cria  **uma única** instância `Redis.from_url(..)`  e a reaproveita em todo o app                       |
| **Decorator genérico** | `app/utils/cache.py → cached_json()`                                                                                    | Função assíncrona que gera chave, consulta Redis (`GET`), serializa JSON (`SETEX`) e devolve resultado  |
| **Aplicação real**     | `app/api/v1/endpoints/local_info.py` <br>`app/api/v1/endpoints/forecast_info.py` <br>`app/api/v1/endpoints/eventos.py`  | Endpoints decorados com `@cached_json("prefix", ttl)`                                                   |
| **Configuração**       | `.env / config.py → REDIS_URL`                                                                                          | Permite apontar para Redis local, Docker, ou nuvem                                                      |

*Exemplo extraído de `local_info.py`:*

```python
@router.get("/local_info", response_model=LocalInfoResponse)
@cached_json("local-info", ttl=86400)       # 24 h
async def obter_local_info(location_name: str, service: AbstractLocalInfoService = Depends(provide_local_info_service)):
    info = await service.get_by_name(location_name)
    if info is None:
        raise HTTPException(404, "Local não encontrado")
    return info
```

---

### 4.3 O que pode ser testado

|  Caso de teste                   |  Objetivo                                                                           |  Ferramentas sugeridas                               |
| -------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **Cache HIT vs MISS**            | Garantir que a primeira requisição (MISS) chama o service/DB e a segunda (HIT) não  | `fakeredis` + pytest → verificar contadores / spies  |
| **TTL expira**                   | Após `ttl` segundos, o decorator deve buscar dados novamente                        | `freezegun` ou `time.sleep` curto                    |
| **Chave única**                  | Requisições com parâmetros diferentes devem gerar chaves diferentes                 | Asset `redis.keys()` contém os hashes esperados      |
| **Fallback se Redis fora do ar** | A aplicação não pode quebrar: decorator executa função original                     | Mock `provide_redis` para levantar `ConnectionError` |

>  **Observação:** nenhum teste precisa de Redis real; use `fakeredis.FakeRedis` e faça override de `provide_redis`.

---

### 4.4 Boas práticas adotadas

\* **TTL adequado** → previsão do tempo 30 min; geocodificação 24 h; rankings de eventos 5–30 s.
\* **Chave determinística** → `prefix` + `hash(args, kwargs)` – minimiza colisões e simplifica invalidar.
\* **Fallback gracioso** → Se Redis cair, o decorator só ignora o cache.
\* **Serialização única** → Sempre JSON string (`default=str`) para uniformidade.

---

### 4.5 Onde alterar caso troque Redis por outro cache

1. Implemente novo provider (`provide_memcached`, por ex.) no mesmo formato.
2. Altere `cached_json` para usar esse provider.
3. Nenhuma rota precisa ser tocada – o decorator cuida de tudo.

---

**TL;DR:** adicionamos Redis para reduzir latência e carga sobre APIs externas com um decorator plug‑and‑play; a própria estrutura permite testar HIT/MISS, TTL e resiliência sem rodar Redis de verdade.


## 4. Cache com Redis para Desempenho

### 4.1 Visão geral

|               |  Sem cache                                      |  Com Redis (cache‑aside)                                                                                            |
| ------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Fluxo         | FastAPI → Service → API externa/banco → Cliente | FastAPI → **Redis GET** → *HIT*? ✔ devolve em 1‑5 ms / *MISS* ✖ → Service → API externa → **Redis SETEX** → Cliente |
| Latência      | 400 ms – 2 s (dependendo da origem)             | 1 ‑ 5 ms após primeiro MISS                                                                                         |
| Carga externa | 100 % das requests                              | ≃ 1 request por TTL                                                                                                 |

> **Estratégia**: *cache‑aside* (também chamado *lazy loading*) – apenas grava no Redis depois de consultar a fonte correta.

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

### 4.4 O que pode ser testado

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

Essa abordagem garante respostas rápidas onde realmente importa, sem aumentar a complexidade nem comprometer a consistência das demais rotas.

Pipeline de Integração Contínua (CI)

Este repositório possui um GitHub Actions workflow (.github/workflows/ci.yml) que automatiza verificações de qualidade toda vez que o código muda. O pipeline protege a main, encurta o ciclo de feedback para colaboradores e documenta a saúde do projeto de forma reproduzível.

Por que investir em CI?

Confiança antes do merge – todo push ou Pull Request (PR) é construído e testado exatamente como em produção.

Feedback rápido – erros de estilo, problemas de tipo ou testes falhando aparecem em minutos.

Cobertura multiplataforma – a matriz executa Ubuntu e Windows em Python 3.10 → 3.12, revelando bugs específicos de SO.

Estilo e segurança automáticos – linters e scanners de segurança comentam direto no PR, liberando os revisores para focarem na regra de negócio.

Qualidade mensurável – relatórios de cobertura acompanham a evolução dos testes ao longo do tempo.

Gatilhos do workflow

Evento

Quando dispara

push

Qualquer commit em main ou develop

pull_request

Novos PRs e cada atualização neles

Rodar nos dois eventos garante que commits isolados fiquem verdes e que o resultado final do merge também passe.

Permissões mínimas

permissions:
  contents: read          # clonar o repositório
  pull-requests: write    # permite que o Ruff / Codecov escrevam comentários

Aplicar apenas o necessário segue o princípio do menor privilégio e reduz riscos na cadeia de suprimentos.

Matriz de execução

Eixo

Valores

Objetivo

OS

ubuntu-latest, windows-latest

Detectar problemas de path/case‑sensitive

Python

3.10, 3.11, 3.12

Garantir compatibilidade futura

O fail-fast: true aborta os demais jobs da matriz após a primeira falha, economizando minutos de build.

Passo a passo

#

Etapa

O que faz

Por que importa

1️⃣

Checkout (actions/checkout)

Clona o código

Torna o fonte disponível no runner

2️⃣

Setup Python (actions/setup-python)

Instala a versão da matriz e restaura cache de pip

Ambiente homogêneo

3️⃣

Cache Poetry + venv

Restaura cache do Poetry e virtualenv se o poetry.lock não mudou

Reduz o tempo de instalação

4️⃣

Instalar dependências

Atualiza pip, instala Poetry e executa poetry install --with dev

Disponibiliza pytest, Ruff etc.

5️⃣

Ruff

Lint + formatação, gera comentários inline

Garante PEP 8, detecta imports não usados e sintaxe antiga

6️⃣

PyUpgrade

Sugere modernização para Python 3.12

Mantém o código atual

7️⃣

MyPy

Checagem estrita de tipos

Encontra erros de contrato antes da execução

8️⃣

Bandit

Linter de segurança

Alerta para eval, md5, injeções…

9️⃣

Pytest

Roda a suíte com -x (fail‑fast) e cobertura ≥ 80 %

Evita regressões

🔟

Codecov (opcional)

Faz upload do coverage.xml e comenta diffs

Métrica de qualidade visível

Cobertura mínima – --cov-fail-under=80 falha o job se a cobertura total cair abaixo de 80 %. Ajuste conforme o projeto amadurece.

Resumo das ferramentas

Ferramenta

Categoria

Comando local

Valor agregado

Ruff

Estilo / análise estática básica

poetry run ruff check .

PEP 8, imports, docstrings

PyUpgrade

Modernização de sintaxe

pyupgrade --py312-plus $(git ls-files '*.py')

Remove legados

MyPy

Tipagem

poetry run mypy app

Previne erros de tipo

Bandit

Segurança

poetry run bandit -q -r app -lll

Detecta padrões inseguros

Pytest

Testes e cobertura

poetry run pytest -x --cov=app

Garante comportamento

Codecov

Cobertura diferencial

Automático pelo Action

Badge + comentários

Execute os mesmos comandos localmente antes do push para obter feedback idêntico ao CI:

poetry install --with dev --no-interaction
poetry run ruff check .
pyupgrade --py312-plus $(git ls-files '*.py')
poetry run mypy app
poetry run bandit -q -r app -lll
poetry run pytest -x --cov=app --cov-fail-under=80

Próximos passos possíveis

Melhoria

Benefício

Observação

CodeQL

Análise de fluxo de dados (SQLi, Path Traversal)

Grátis em repositórios públicos

Dependabot

PRs automáticos para libs vulneráveis

dependabot.yml semanal

pre‑commit

Mesmos linters rodando no hook local

Evita rodadas de CI perdidas

Build de Docker

Publica imagem em cada tag

docker/build-push-action

Release‑drafter

Gera CHANGELOG automaticamente

Ajuda no versionamento

Artefatos

Armazena relatórios HTML, wheels

actions/upload-artifact

Notificações Slack

Status do CI no chat

8398a7/action-slack

Referência de configuração (trecho)

[tool.ruff]
line-length = 250

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
ignore = ["E241", "E302", "E231", "E226", "E261", "E262", "E305", "E251", "I001"]
extend-ignore = ["D203", "D213"]
preview = true

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

Simulando o workflow localmente (opcional)

Com act:

act push --job test

O act roda um contêiner Docker que imita o ubuntu-latest, devolvendo resultados quase idênticos ao CI real sem esperar na fila.

Bom código – e aproveite a rede de segurança! 🚀

📊 Observabilidade e Logs
Este projeto conta com um sistema estruturado e extensível de logs usando structlog, permitindo registros claros, padronizados e prontos para ferramentas de monitoramento, auditoria e diagnóstico.

✅ Funcionalidades Implementadas
Log estruturado com structlog, no formato JSON.

Middleware de logging que registra todas as requisições HTTP com:

Método (GET, POST, etc.)

Caminho (/api/v1/...)

Código de status da resposta (200, 404, etc.)

Duração da requisição (em segundos)

IP do cliente

Cabeçalho User-Agent

Usuário autenticado (quando houver)

Contexto global por requisição com ContextVar (request_user) para registrar o nome do usuário logado ao longo da requisição.

Filtragem de rotas internas: rotas como /docs, /redoc e /openapi.json são ignoradas nos logs para evitar ruído.

🧱 Estrutura de Arquivos
Arquivo	Função
app/core/logging_config.py	Configuração do structlog (formato JSON, timestamp, nível de log etc.)
app/core/contextvars.py	Define a variável request_user para guardar o usuário da requisição
app/services/auth_service.py	Define o request_user após autenticação via token
app/middleware/logging_middleware.py	Middleware que registra cada requisição HTTP, incluindo usuário
Diversos mock_*.py, event_mem.py, deps.py	Logs internos de operações simuladas e repositórios

🧩 Exemplo de log gerado
json
Copiar
Editar
{
  "event": "HTTP request log",
  "method": "GET",
  "path": "/api/v1/eventos",
  "status_code": 200,
  "duration": 0.015,
  "client": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "user": "alice",
  "timestamp": "2025-06-15T18:00:00Z",
  "level": "info"
}
🛠 Como estender
Você pode ampliar o sistema de logs com as seguintes práticas:

Logar o tamanho da resposta (bytes).

Registrar os corpos da requisição/resposta (útil para debugging — evite dados sensíveis).

Enviar os logs para ferramentas externas como Loki, ELK (Elasticsearch + Logstash + Kibana) ou DataDog.

Separar logs de erro em arquivos distintos.

Adicionar um ID de correlação por requisição para rastrear logs em microsserviços.

📌 Dicas
Os logs são estruturados e podem ser consumidos facilmente por ferramentas como Grafana, Prometheus, Loki ou ElasticSearch.

Utilize logger.info(...), logger.warning(...) e logger.error(...) em qualquer ponto do sistema: a estrutura já está preparada para manter os logs padronizados e legíveis.

## 📡 WebSockets, Upload e Download de Arquivos

Esta seção descreve como foram implementadas as funcionalidades relacionadas a tempo real e manipulação de arquivos no projeto, detalhando o uso de WebSockets e rotas para upload e download de arquivos.

### 1. WebSockets

O WebSocket permite uma comunicação interativa e em tempo real entre o servidor e os clientes conectados, possibilitando notificações instantâneas, progresso em tempo real e atualizações de dashboards.

#### Funcionalidades via WebSocket:

* **Upload de Eventos em Tempo Real:**

  * Notificações de progresso linha a linha durante o upload.
  * Indicação imediata de erros por linha.
  * Mensagem final ao término da importação.

* **Dashboard ao Vivo:**

  * Contagem de eventos atualizada automaticamente sem necessidade de polling HTTP.
  * Número de usuários conectados atualizado em tempo real.

* **Logs e Status de Tarefas Longas:**

  * Envio contínuo de logs ou mensagens de status enquanto tarefas são executadas.

* **Notificações Administrativas:**

  * Avisos aos administradores sempre que novos eventos forem criados ou houver alterações massivas.

### 2. Upload de Eventos via CSV

Implementado um endpoint `/eventos/upload` para permitir o upload de arquivos CSV contendo múltiplos eventos. Cada linha do CSV representa um evento completo que será processado e adicionado ao repositório.

* Formato esperado do CSV:

```csv
title,description,event_date,city,participants,local_info
Evento 1,Descrição do evento,2025-07-01T10:00:00,Recife,Alice;Bob,"{\"location_name\": \"Auditório Central\", \"capacity\": 300, \"venue_type\": \"Auditório\", \"is_accessible\": true, \"address\": \"Rua Exemplo, 123\", \"past_events\": [], \"manually_edited\": false}"
```

* Durante o upload:

  * Validação das linhas do arquivo.
  * Retorno detalhado via WebSocket sobre o status e possíveis erros.

### 3. Download de Eventos em JSON

Foi criado um endpoint `/eventos/download` que permite baixar os eventos existentes no repositório em formato JSON.

* Exemplo do endpoint:

```http
GET /api/v1/eventos/download
```

* A resposta será um arquivo JSON contendo todos os eventos cadastrados:

```json
[
  {
    "title": "Evento 1",
    "description": "Descrição do evento",
    "event_date": "2025-07-01T10:00:00",
    "city": "Recife",
    "participants": ["Alice", "Bob"],
    "local_info": {
      "location_name": "Auditório Central",
      "capacity": 300,
      "venue_type": "Auditório",
      "is_accessible": true,
      "address": "Rua Exemplo, 123",
      "past_events": [],
      "manually_edited": false
    }
  }
  // Mais eventos...
]
```

Essas funcionalidades ampliam significativamente a interatividade e eficiência do projeto, oferecendo feedback instantâneo e facilitando operações em lote por meio de arquivos.

🧪 Testes Automatizados
O projeto utiliza testes automatizados com pytest para garantir a confiabilidade e robustez do sistema, garantindo também que as novas funcionalidades não quebrem implementações existentes. Os testes abrangem tanto testes unitários quanto testes de integração, com medição de cobertura utilizando pytest-cov.

🔧 Decisões técnicas para os testes
Durante o desenvolvimento dos testes, foram encontrados cenários específicos que geraram erros de execução, especialmente relacionados à criação de tarefas assíncronas usando a função asyncio.create_task() em rotas síncronas.

Para resolver isso mantendo a integridade do código principal (o sistema já estava em produção e funcionando corretamente), foi tomada a decisão de ajustar exclusivamente o comportamento dos testes ao invés do código da aplicação.

Motivos da decisão:

O sistema em produção estava funcionando corretamente.

Alterações no código principal poderiam impactar negativamente o ambiente produtivo.

O problema era específico dos testes, que executavam em contextos síncronos onde não havia um event loop ativo.

⚙️ Alteração Realizada nos Testes
A alteração foi feita diretamente na configuração dos testes (no arquivo tests/conftest.py), utilizando o recurso monkeypatch do pytest para substituir a função problemática durante a execução dos testes:

Função substituída: asyncio.create_task

Motivo: Durante testes, esta função lançava RuntimeError: no running event loop, já que o pytest executava as chamadas síncronas em um contexto sem event loop ativo.

Antes:
python
Copiar
Editar
asyncio.create_task(coroutine)
Depois (apenas nos testes):
python
Copiar
Editar
def _safe_create_task(coro, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(coro, *args, **kwargs)
    except RuntimeError:
        _loop = asyncio.new_event_loop()
        try:
            _loop.run_until_complete(coro)
        finally:
            _loop.close()

        class _DummyTask:
            def cancel(self):
                pass
        return _DummyTask()

monkeypatch.setattr(asyncio, "create_task", _safe_create_task, raising=True)
Essa solução garante que:

Caso já exista um event loop ativo, o comportamento padrão de asyncio.create_task() é mantido.

Caso contrário (cenário de testes síncronos), é criado um novo event loop temporário para executar o coroutine diretamente, garantindo a execução e evitando erros durante o teste.

📌 Funções Impactadas e Testes Relacionados
As funções do sistema afetadas e ajustadas especificamente para testes foram:

put_events (rota /eventos), que dispara tarefas assíncronas como notificações WebSocket.

post_create_event (rota POST /eventos), que dispara notificações assíncronas após criar eventos.

Essas funções são testadas pelos seguintes testes, entre outros:

test_create_event_valid

test_replace_all_events

test_update_event_type_valid

test_update_local_info

test_atualizar_forecast_info

Dessa forma, os testes foram corrigidos sem nenhuma alteração funcional ou estrutural no código da aplicação, preservando o comportamento original do sistema e garantindo testes estáveis e confiáveis.

migrations

2. Recrie a migração corretamente
Como a migração anterior não criou a tabela events, você precisa apagar essa versão e gerar outra:

bash
Copiar
Editar
# 1. Apague o migration antigo (ou renomeie para backup)
rm migrations/versions/*.py  # cuidado: isso remove TODAS as versões de migração

# 2. Gere nova migração com os modelos agora corretamente importados
alembic revision --autogenerate -m "create tables"

# 3. Aplique a nova migração
alembic upgrade head

Esse erro aconteceu porque você deletou ou removeu os arquivos da pasta migrations/versions/, mas o banco de dados ainda está com o controle interno apontando para a versão 'e69fdb78a658'.

✅ Como resolver isso corretamente
📌 Objetivo:
Resetar o histórico de migrações para sincronizar o banco com a nova estrutura de arquivos.

✅ Etapas para resolver:
1. Apague a tabela de controle de migração (alembic_version)
Essa tabela fica no seu banco de dados e guarda qual versão está atualmente aplicada. Execute no seu banco (via psql, DBeaver, pgAdmin, ou terminal):

sql
Copiar
Editar
DROP TABLE alembic_version;
Isso permite que o Alembic recrie o controle corretamente com a nova versão.

2. Crie uma nova migração do zero
Com os modelos devidamente importados no migrations/env.py, rode:

bash
Copiar
Editar
alembic revision --autogenerate -m "create all tables"
Isso vai gerar um novo arquivo de migração em migrations/versions/.

3. Aplique essa nova migração ao banco
bash
Copiar
Editar
alembic upgrade head
Se tudo estiver correto, agora a tabela events e as outras (local_infos, forecast_infos) serão criadas.