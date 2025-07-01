---

## 🎯 Objetivo Geral

O objetivo principal do FastTrackAPI é capacitar desenvolvedores e estudantes em práticas modernas de backend, oferecendo um ambiente estruturado e próximo de aplicações reais, onde é possível aplicar conceitos teóricos em situações práticas e comuns no mercado atual.

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
  - [ ] Orquestrar serviços com Docker Compose (app, banco, redis)
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

[⬅️ Voltar para o início](../README.md)
