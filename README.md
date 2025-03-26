# FastTrackAPI – Projeto Prisma

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
  - [ ] Criar rotas RESTful com métodos GET, POST, PUT, DELETE
  - [ ] Utilizar `Depends` para injeção de dependências
  - [ ] Validar dados de entrada e saída com Pydantic
  - [ ] Utilizar tags, responses e exemplos para a documentação automática
  - [ ] Implementar Background Tasks
  - [ ] Trabalhar com WebSockets
  - [ ] Fazer upload e download de arquivos

- [ ] **Aplicar arquitetura de software adequada para aplicações backend**
  - [ ] Organizar a aplicação em camadas (router, service, repository, schema, model)
  - [ ] Aplicar princípios SOLID, DRY, KISS e YAGNI
  - [ ] Criar dependências reutilizáveis e testáveis
  - [ ] Adotar um padrão de projeto para escalar o backend

- [ ] **Implementar boas práticas de segurança no backend**
  - [ ] Utilizar autenticação com JWT
  - [ ] Implementar autorização com escopos e permissões
  - [ ] Proteger rotas com `Depends` e lógica de verificação
  - [ ] Armazenar senhas com hash seguro (bcrypt, passlib)
  - [ ] Prevenir vulnerabilidades comuns (SQL Injection, XSS, etc)

- [ ] **Utilizar ferramentas e práticas de DevOps no fluxo de desenvolvimento**
  - [ ] Utilizar Docker para empacotar a aplicação
  - [ ] Orquestrar serviços com Docker Compose (app, banco, redis)
  - [ ] Criar pipelines de CI com GitHub Actions (teste e lint automático)
  - [ ] Rodar migrations de banco em containers (ex: Alembic via Compose)

- [ ] **Gerenciar configurações de forma segura e flexível**
  - [ ] Utilizar `.env` com Pydantic Settings
  - [ ] Separar configurações por ambiente (dev, prod, test)
  - [ ] Garantir fallback seguro para variáveis obrigatórias

- [ ] **Desenvolver testes automatizados**
  - [ ] Criar testes unitários com `pytest`
  - [ ] Implementar testes de integração simulando requisições reais
  - [ ] Utilizar mocks para isolar dependências em testes
  - [ ] Medir cobertura de código com `pytest-cov`

- [ ] **Adicionar observabilidade e monitoramento à aplicação**
  - [ ] Adicionar logs estruturados com `loguru` ou `structlog`
  - [ ] Criar middlewares para registrar requisições/respostas
  - [ ] Monitorar erros e alertas (integração futura com ferramentas externas)

- [ ] **Documentar a API e o projeto de forma clara e profissional**
  - [ ] Aproveitar documentação automática do Swagger/OpenAPI
  - [ ] Adicionar exemplos e descrições nos modelos Pydantic
  - [ ] Manter um `README.md` atualizado e bem estruturado

- [ ] **Aprofundar o uso de banco de dados com SQLAlchemy**
  - [ ] Criar modelos ORM com relacionamentos
  - [ ] Escrever queries mais avançadas (joins, agregações)
  - [ ] Implementar filtros e paginação em endpoints
  - [ ] Gerenciar migrações com Alembic

- [ ] **Trabalhar com versionamento de código no GitHub com boas práticas**
  - [ ] Utilizar branches e pull requests para organizar o fluxo de trabalho
  - [ ] Escrever mensagens de commit claras e informativas
  - [ ] Resolver conflitos de merge com segurança

- [ ] **Explorar funcionalidades avançadas conforme a evolução do projeto**
  - [ ] Usar cache com Redis para otimização de desempenho
  - [ ] Realizar deploy em nuvem (Render, Railway ou VPS)
  - [ ] Testar uso de workers com Celery ou RQ (tarefa opcional)
  - [ ] Expor métricas básicas (ex: Prometheus ou logs customizados)

---

## 🗂️ Estrutura de Pastas

```bash
fasttrackapi-projeto-prisma/
├── app/
│   ├── api/                    # Rotas da API (FastAPI Routers)
│   │   ├── v1/                 # Versão da API
│   │   │   ├── endpoints/      # Endpoints específicos (ex: user.py)
│   │   │   └── api_router.py   # Agrupa todos os endpoints da v1
│   ├── core/                   # Configurações globais da aplicação
│   │   ├── config.py           # Carrega variáveis de ambiente com Pydantic
│   │   └── security.py         # Configurações relacionadas à segurança/autenticação
│   ├── models/                 # Modelos do banco de dados (SQLAlchemy)
│   ├── schemas/                # Modelos de entrada/saída (Pydantic)
│   ├── services/               # Lógica de negócio
│   ├── repositories/           # Funções de acesso ao banco de dados
│   ├── utils/                  # Funções auxiliares
│   ├── main.py                 # Ponto de entrada da aplicação FastAPI
│   └── deps.py                 # Dependências compartilhadas (ex: get_db)
│
├── tests/
│   ├── unit/                   # Testes unitários
│   ├── integration/            # Testes de integração (rotas completas)
│   └── conftest.py             # Configurações e fixtures para testes
│
├── .env                        # Variáveis de ambiente (não versionado)
├── .env.example                # Exemplo de variáveis para replicar o ambiente
├── Dockerfile                  # Imagem Docker da aplicação
├── docker-compose.yml          # Orquestração com banco de dados e Redis
├── pyproject.toml              # Gerenciado pelo Poetry (dependências, versão, etc)
├── poetry.lock                 # Trava das versões instaladas
├── README.md                   # Documentação principal do projeto
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

- **EventoCriacao**: utilizado ao criar um novo evento. Permite inserir os dados principais, e os campos `local_info` e `forecast_info` são opcionais.
- **EventoAtualizacao**: utilizado para atualizar os dados de um evento após a criação. Exige os campos `local_info` e `forecast_info`, que contêm dados externos.
- **LocalInfo**: estrutura esperada da API simulada com dados sobre o local do evento, como capacidade, tipo, acessibilidade e endereço.
- **PrevisaoClima**: estrutura que representa os dados retornados pela API pública de previsão do tempo.

Todos esses modelos estão localizados na pasta `app/schemas/` e são essenciais para garantir a validação de dados, a integridade da aplicação e a geração automática da documentação da API via OpenAPI/Swagger.

---