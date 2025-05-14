#!/bin/bash
# Inicia o ambiente local usando Poetry e executa a aplicação FastAPI

# Verifica se o poetry está instalado
if ! command -v poetry &> /dev/null
then
    echo "Poetry não encontrado. Instale com: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Instala dependências e entra no shell
poetry install

# Executa a aplicação com reload
poetry run uvicorn app.main:app --reload