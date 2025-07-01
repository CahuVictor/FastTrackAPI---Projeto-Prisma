# Em construção
# ⚙️ Pipeline de Integração Contínua (CI)

O projeto **FastTrackAPI** utiliza uma pipeline de integração contínua (CI) para garantir qualidade, rastreabilidade e segurança em cada mudança submetida ao repositório.

---

## 📁 Estrutura da Pipeline

A pipeline está dividida em etapas executadas automaticamente em cada `push` ou `pull request` para o repositório principal:

### 1. ✅ **Verificação de Sintaxe e Formatação**

* Verifica se o código segue o estilo definido (ex: `black`, `isort`, `flake8`).
* Garante padronização para facilitar revisão e leitura.

### 2. 🔍 **Testes Automatizados**

* Executa os testes unitários e de integração com `pytest`.
* Usa `pytest-cov` para gerar relatórios de cobertura.

### 3. 🌐 **Verificação de Tipos**

* Utiliza `mypy` para garantir coerência dos tipos estáticos no projeto.

### 4. 🚷 **Segurança e Dependências**

* Verifica vulnerabilidades conhecidas com `safety` ou `bandit`.
* Checa se arquivos `pyproject.toml` e `poetry.lock` estão atualizados.

---

## 📊 Exemplo de Configuração GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Instalar dependências
        run: |
          pip install poetry
          poetry install
      - name: Rodar testes
        run: poetry run pytest --cov=app
      - name: Verificação de tipo
        run: poetry run mypy app/
      - name: Análise de segurança
        run: poetry run bandit -r app/
```

---

## 🔧 Extensões Futuras

* Deploy automático para ambientes de staging/homologação.
* Geração automática de documentação.
* Publicação de imagens Docker e versionamento.

---

## 🚀 Benefícios

* Detecção precoce de erros.
* Redução de falhas em produção.
* Feedback rápido para desenvolvedores.
* Cultura de qualidade e segurança.

---

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

---

[⬅ Voltar para o índice](../README.md)
