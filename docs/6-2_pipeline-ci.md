# ⚙️ Continuous Integration (CI) Pipeline – *FastTrackAPI*

O **FastTrackAPI** adota uma *pipeline* de Integração Contínua (CI) baseada em **GitHub Actions** para garantir qualidade, rastreabilidade e segurança a cada *push* ou *pull request*.

---

## 📁 Visão geral da pipeline

| Etapa                                 | Ferramenta              | Propósito                                              |
| ------------------------------------- | ----------------------- | ------------------------------------------------------ |
| **1. Lint & Formatting**              | **Ruff (+ PyUpgrade)**  | PEP‑8, ordenação de imports, remoção de sintaxe legada |
| **2. Type‑checking**                  | **MyPy**                | Coerência estática dos `type hints`                    |
| **3. Security Scan**                  | **Bandit**              | Busca por CWEs ( `eval`, `md5`, *shell =True* … )      |
| **4. Testes & Cobertura**             | **Pytest + pytest‑cov** | Testes unitários/integrados com *coverage ≥ 80 %*      |
| **5. Upload de cobertura** (não implementado) | **Codecov**             | Badge e *diff* de cobertura nos PRs                    |

> **Fail‑fast**: a matriz (SO × Python) para assim que encontra a 1ª falha, economizando minutos de execução.

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

1️⃣ MyPy – verificador de type hints

Analisa os type hints do Python (def foo(x: int) -> str:) e compara com o fluxo real do código. Encontra incongruências de tipos antes de você rodar o programa.

2️⃣ Bandit – linter de segurança

Avalia source Python em busca de “Common Weaknesses” (CWE): ‣ uso de eval, ‣ chaves criptográficas hard-coded, ‣ subprocess sem shell=False, ‣ hashlib.md5, etc.


3️⃣ PyUpgrade – modernizador de sintaxe

Reescreve automaticamente trechos antigos para a versão Python que você escolher.

4️⃣ CodeQL – análise de vulnerabilidade mantida pelo GitHub

Compila seu projeto para um grafo semântico e executa consultas (“queries”) que detectam padrões inseguros, SQL-Injection, Path-Traversal etc.
É a solução oficial de Code Scanning do GitHub Advanced Security (grátis em repositórios públicos).

5️⃣ Dependabot (Security Spotlight)

Serviço do GitHub que cria Pull Requests automáticos quando sai versão nova (ou patch de segurança) de dependências.

--

## 🌐 Gatilhos do workflow

```yaml
on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main", "develop" ]
```

Executado no commit direto e em PRs, garantindo que o merge final também passe.

---

## 🔐 Permissões mínimas

```yaml
permissions:
  contents: read        # checkout
  pull-requests: write  # comentários do Ruff / Codecov
```

Aderimos ao **princípio do menor privilégio**.

---

## 🖥️ Matriz de execução

| Eixo       | Valores                           | Objetivo                                      |
| ---------- | --------------------------------- | --------------------------------------------- |
| **OS**     | `ubuntu-latest`, `windows-latest` | Detectar problemas de *path* / case‑sensitive |
| **Python** | `3.10`, `3.11`, `3.12`            | Garantir compatibilidade futura               |

> `fail-fast: true` aborta os demais jobs da matriz se a primeira combinação falhar.

---

## 📜 Passo‑a‑passo do job `test`

| #   | Etapa                     | Ação / Comando                                                                               | Por quê                            |
| --- | ------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------- |
| 1️⃣ | **Checkout**              | `actions/checkout@v4`                                                                        | Disponibiliza o fonte no runner    |
| 2️⃣ | **Setup Python**          | `actions/setup-python@v5` + cache de `pip`                                                   | Ambiente reproduzível              |
| 3️⃣ | **Cache Poetry + venv**   | `actions/cache@v4`                                                                           | Acelera builds (\~ 60 %)           |
| 4️⃣ | **Instalar dependências** | `poetry install --with dev`                                                                  | Disponibiliza todas as ferramentas |
| 5️⃣ | **Ruff**                  | `poetry run ruff check --output-format=github .`                                             | Lint + comentários inline          |
| 6️⃣ | **PyUpgrade**             | `poetry run pyupgrade --py312-plus --exit-zero-even-if-changed $(git ls-files '*.py')`       | Sugere modernização                |
| 7️⃣ | **MyPy**                  | `poetry run mypy app`                                                                        | Checagem estrita de tipos          |
| 8️⃣ | **Bandit**                | `poetry run bandit -q -r app -lll`                                                           | Scanner de segurança               |
| 9️⃣ | **Pytest + coverage**     | `poetry run pytest           | Garante cobertura mínima           |
| 🔟  | **Codecov**               | `codecov/codecov-action@v4`                                                                  | Badge & *diff* de cobertura        |

---

## 🛠️ Ferramentas & comandos locais

| Ferramenta    | Categoria     | Comando                                              |
| ------------- | ------------- | ---------------------------------------------------- |
| **Ruff**      | Lint + Format | `poetry run ruff check .`                            |
| **PyUpgrade** | Modernização  | `pyupgrade --py312-plus $(git ls-files '*.py')`      |
| **MyPy**      | Tipagem       | `poetry run mypy app`                                |
| **Bandit**    | Segurança     | `poetry run bandit -q -r app -lll`                   |
| **Pytest**    | Testes        | `poetry run pytest -x                                |

Execute esses comandos localmente antes do *push* para obter feedback idêntico ao CI.

---

## 🎯 Exemplo completo de workflow (`.github/workflows/ci.yml`)

```yaml
ame: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

permissions:
  contents: read
  pull-requests: write

jobs:
  test:
    strategy:
      fail-fast: true
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    runs-on: ${{ matrix.os }}

    env:
      PYTHON_KEYRING_BACKEND: keyring.backends.fail.Keyring
      ENVIRONMENT: test

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pypoetry
            ~/.virtualenvs
          key: ${{ runner.os }}-poetry-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install --with dev --no-interaction

      - name: Ruff
        run: poetry run ruff check --output-format=github .

      - name: PyUpgrade
        run: poetry run pyupgrade --py312-plus --exit-zero-even-if-changed $(git ls-files '*.py')

      - name: MyPy
        run: poetry run mypy app

      - name: Bandit
        run: poetry run bandit -q -r app -lll

      - name: Pytest
        run: |
          poetry run pytest

      - name: Upload coverage to Codecov
        if: success()
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

---

## ⚠️ Conflitos de Docstring (D203 × D211, D212 × D213)

Os pares de regras abaixo se anulam; declaramos *ignore* para o segundo par no `pyproject.toml`:

| Regra  | Resumo                                                  | Conflita com |
| ------ | ------------------------------------------------------- | ------------ |
| `D203` | Requer linha em branco **antes** da docstring de classe | `D211`       |
| `D211` | Não pode haver linha em branco **antes** da docstring de classe | `D203`       |
| `D212` | Para docstring multilinha, o resumo deve iniciar na primeira linha | `D213`       |
| `D213` | Para docstring multilinha, o resumo deve iniciar na segunda linha | `D212`       |

---

## 🕹️ Patch específico de testes ( `asyncio.create_task` )

Nos testes unitários, rotas síncronas chamavam `asyncio.create_task()` e geravam `RuntimeError: no running event loop`.
Foi aplicado um **monkeypatch** em `tests/conftest.py`:

```python
import asyncio

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

pytest.monkeypatch.setattr(asyncio, "create_task", _safe_create_task, raising=True)
```

Isso preserva o comportamento em produção e estabiliza a suíte de testes.

---

## 🐞 Correção recente – *timezone‑aware*

Um `TypeError` surgiu ao comparar `datetime.utcnow()` (naive) com objetos *aware*.
Foi corrigido trocando:

```python
now = datetime.utcnow()
```

por

```python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```

no endpoint **GET /eventos/top/soon**.

---

## 🔮 Próximas melhorias

| Item                    | Benefício                              | Observação                      |
| ----------------------- | -------------------------------------- | ------------------------------- |
| **CodeQL**              | Varredura de vulnerabilidades avançada | Grátis em repositórios públicos |
| **Dependabot**          | PRs automáticos de atualização         | `dependabot.yml` semanal        |
| **pre‑commit**          | Linters locais antes do *push*         | Evita CI falhar por estilo      |
| **Docker Build & Push** | Imagem publicada a cada tag            | `docker/build-push-action`      |
| **Release‑drafter**     | CHANGELOG automático                   | Facilita versionamento          |
| **Slack notify**        | Status do CI no chat                   | `8398a7/action-slack`           |

* Deploy automático para ambientes de staging/homologação.
* Geração automática de documentação.

---

## 📚 Referências de configuração

```toml
[tool.ruff]
line-length = 100                     # segue no nível raiz (formatação)

[tool.ruff.lint]                      # ⬅️ tudo abaixo diz respeito ao *linter*
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

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
```

---

## 💻 Rodando tudo localmente

Rodar testes localmente igual ao CI
# 1ª vez
  poetry install --with dev --no-interaction
# sempre que for commitar
  poetry run pytest

Adicione a dependência no grupo dev para rodar localmente:
  poetry add --group dev ruff

```bash
poetry install --with dev --no-interaction
poetry run ruff check .
poetry run pyupgrade --py312-plus $(git ls-files '*.py')
poetry run mypy app
poetry run bandit -q -r app -lll
$env:ENVIRONMENT = "test.inmemory"
poetry run pytest -x
```

Se não ativar o test.inmemory, os testes dão erro, precisa analisar depois como corrigir, mas de momento podemos focar em habilitar este modo para o teste.

Para simular o workflow GitHub Actions sem sair do terminal:

```bash
act push --job test
```

---

[⬅ Voltar para o Índice](../README.md)