# FastTrackAPI – Projeto Prisma

Este repositório faz parte de uma mentoria prática de backend com Python e FastAPI.  
O **Projeto Prisma** representa a construção de uma base sólida e estruturada, refletindo a clareza e a organização de um backend bem projetado.

A proposta do **FastTrackAPI** é acelerar o aprendizado, explorando na prática os principais pilares do desenvolvimento backend moderno.

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

Seja bem-vindo(a) ao Prisma, uma jornada prática para dominar o backend com clareza e boas práticas 🚀
