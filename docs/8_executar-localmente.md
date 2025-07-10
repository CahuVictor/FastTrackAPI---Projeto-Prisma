# ▶️ Executar Localmente

Este guia apresenta diferentes formas de rodar o projeto **FastTrackAPI — Projeto Prisma** no ambiente local, de acordo com o nível de complexidade e os serviços necessários.

---

## 🧱 Pré-requisitos

Antes de começar, certifique-se de ter:

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker + Docker Compose (recomendado para rodar Redis e banco em container)
- Git
- Redis local (para cenários mais simples)

---

## ⚙️ Cenário 1 – Execução com dados em memória (`ENVIRONMENT=test.inmemory`)

Ideal para testes rápidos e desenvolvimento inicial. Apenas o Redis precisa estar disponível localmente.

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/FastTrackAPI---Projeto-Prisma.git
cd FastTrackAPI---Projeto-Prisma

# Instale dependências
poetry install

# A partir do Poetry 2.0, o comando poetry shell não vem instalado por padrão.
# Para usar este comando  instale o plugin com:
poetry self add poetry-plugin-shell

# O PowerShell inicializa com a política de execução de scripts desabilitada, o que impede que o script activate.ps1 (usado para ativar o ambiente virtual) seja executado.
# Para liberar temporariamente (só para a sessão atual do PowerShell):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Ative o ambiente do poetry
poetry shell

# Certifique-se de que o Redis está rodando localmente na porta padrão
# Ex: redis-server (ou via Docker)

# Execute a aplicação no Windows
# Defina a variável de ambiente temporária
$env:ENVIRONMENT = "test.inmemory"
uvicorn app.main:app --reload

# Se não tiver sendo chamado pelo ambiente virtual, chame explicitamente o poetry
poetry run uvicorn app.main:app

# Execute a aplicação no Linux/macOS
ENVIRONMENT=test.inmemory uvicorn app.main:app --reload
```

Acesse:
- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚙️ Cenário 2 – Execução com banco de dados em container (`ENVIRONMENT=dev`)

Neste modo, os dados são persistidos em um container de banco. Ideal para testar persistência e queries reais.

```bash
# Suba os containers (Banco)
docker-compose up -d db

# Instale dependências e ative ambiente
poetry install
poetry shell

# Execute a API localmente
uvicorn app.main:app --reload
```

---

## ⚙️ Cenário 3 – Execução com banco + Redis via containers (`ENVIRONMENT=dev`)

Ideal para testar toda a stack com banco de dados e cache local, mantendo a aplicação principal fora do Docker.

```bash
# Suba banco e Redis via Docker
docker-compose up -d db redis

# Execute a aplicação localmente com poetry
poetry install
poetry shell

# Execute a API localmente
uvicorn app.main:app --reload
```

---

## ⚙️ Cenário 4 – Todos os serviços em container (`ENVIRONMENT=prod` ou `dev`)

Aqui, toda a aplicação roda em containers. Ideal para simular um ambiente de produção.

```bash
# Atualizar o ENV para prod ou dev

# Suba tudo via Docker
docker-compose up --build
```

Acesse:
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌍 Cenário futuro – Integração com API externa de localização e clima

Os serviços já estão definidos por contrato (`Protocol`) e podem ser ativados em produção ou desenvolvimento com backends reais.

### Como usar

- **Para Local Info**:
  - Configure `LOCAL_INFO_API_URL` no `.env`
- **Para Previsão do Tempo**:
  - Configure `FORECAST_API_URL` no `.env`
- Substitua os serviços mocks por implementações reais em `deps.py`.

---

## 📦 Rodando os testes
## ✅ Execução de Testes

```bash
ENVIRONMENT=test poetry run pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-report=html
```

- Visualize em: `htmlcov/index.html`

---

## 🔐 Acesso com autenticação

A autenticação utiliza JWT. Para obter um token:

1. Faça login via `/auth/login` com usuário e senha.
2. Use o token no header:  
   `Authorization: Bearer SEU_TOKEN`

**Usuários de teste disponíveis:**

| Usuário | Senha      | Papel   |
|--------|------------|---------|
| alice  | secret123  | admin   |
| bob    | builder123 | editor  |
| carol  | pass123    | viewer  |

---

## 🧪 Variáveis de Ambiente

Você pode definir variáveis no `.env`, `.env.dev`, `.env.test`, `.env.test.inmemory` ou `.env.prod`. Exemplo:

```env
ENVIRONMENT=dev
REDIS_URL=redis://localhost:6379/0
DB_URL=sqlite:///dev.db
AUTH_SECRET_KEY=uma_chave_secreta
```

---

## 🔗 Endpoints Úteis

- `/docs` – Interface interativa Swagger UI  
- `/redoc` – Documentação alternativa  
- `/health` – Verifica se a API está online  
- `/ws/eventos/progresso` – WebSocket para progresso em tempo real

---

[⬅️ Voltar para o índice](../README.md)
