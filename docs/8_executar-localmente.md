# Em construção
# ▶️ Executar Localmente

Este guia descreve como rodar o projeto **FastTrackAPI** no ambiente local para fins de desenvolvimento e testes.

---

## 🧱 Pré-requisitos

Antes de iniciar, verifique se você possui os seguintes itens instalados:

* Python 3.12+
* [Poetry](https://python-poetry.org/)
* Docker e Docker Compose (opcional, mas recomendado para dependências como Redis)
* Git

---

## 🚀 Etapas para execução

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/FastTrackAPI.git
cd FastTrackAPI
```

### 2. Instale as dependências com Poetry

```bash
poetry install
```

### 3. Ative o ambiente virtual do Poetry

```bash
poetry shell
```

### 4. Rode a aplicação FastAPI

```bash
uvicorn app.main:app --reload
```

O servidor será iniciado em [http://localhost:8000](http://localhost:8000)

---

## 🐋 Executando com Docker

### 1. Suba os containers

```bash
docker-compose up --build
```

### 2. Acesse o app

* API: [http://localhost:8000](http://localhost:8000)
* Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Rodando os testes

### Testes com cobertura:

```bash
poetry run pytest --cov=app --cov-report=html
```

Abra o arquivo `htmlcov/index.html` no navegador para visualizar a cobertura.

---

## 🧪 Variáveis de Ambiente

Você pode definir variáveis no arquivo `.env` ou diretamente no terminal:

```env
APP_ENV=development
REDIS_URL=redis://localhost:6379
SECRET_KEY=uma_chave_secreta
```

---

## 🧰 Endpoints úceis

* `/docs` – Interface interativa Swagger UI
* `/redoc` – Interface alternativa da documentação
* `/health` – Verifica se a API está no ar
* WebSocket: `/ws/eventos/progresso` – Recebe atualizações em tempo real

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

---

[⬅️ Voltar para o índice](../README.md)
