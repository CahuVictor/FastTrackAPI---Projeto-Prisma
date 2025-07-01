# ✅ Testes Automatizados

A qualidade do projeto **FastTrackAPI** é garantida através de uma cobertura robusta de testes automatizados, que asseguram o correto funcionamento das funcionalidades e permitem evoluir o sistema com confiança.

---

## 🧪 Tipos de Testes

O projeto está organizado com dois principais tipos de testes:

### 🔹 Testes Unitários

* Validam funções e lógicas isoladas.
* Incluem testes para schemas Pydantic, validações e normalizações.
* Simulam chamadas de API com dados esperados e inválidos.

### 🔸 Testes de Integração

* Validam o funcionamento conjunto das rotas com serviços auxiliares.
* Testam fluxos completos como:

  * Criação e consulta de eventos.
  * Atualização e deleção de dados.
  * Rotas com WebSockets.

Todos os testes estão organizados em `tests/unit/` e usam convenção `test_*.py`.

---

## ⚙️ Ferramentas Utilizadas

| Ferramenta           | Função                                 |
| -------------------- | -------------------------------------- |
| `pytest`             | Execução de testes e asserções.        |
| `pytest-cov`         | Gera relatório de cobertura de código. |
| `httpx.AsyncClient`  | Testes assíncronos de rotas.           |
| `fastapi.testclient` | Simula chamadas HTTP sincrônas.        |

---

## 🔁 Fixtures e Parametrização

Para facilitar o reuso de dados e evitar repetições:

* Dados comuns estão centralizados em `tests/conftest.py`.
* Fixtures como `evento_valido` e `client` permitem criar testes concisos.
* A função `@pytest.mark.parametrize` permite rodar o mesmo teste com múltiplos dados.

---

## 📊 Cobertura de Testes

A cobertura atual é medida com o comando:

```bash
poetry run pytest --cov=app --cov-report=html
```

* Um relatório interativo é gerado em `htmlcov/index.html`.
* O objetivo é manter cobertura superior a **85%**.

---

## ❌ Testes de Fluxos Inválidos

Todos os endpoints também possuem cenários negativos:

* Requisições com dados inválidos (`422 Unprocessable Entity`).
* Requisição de recursos inexistentes (`404 Not Found`).
* Acesso não autorizado (em endpoints protegidos).

Esses testes validam a robustez das validações e mensagens de erro.

---

## 🧰 Exemplo de Teste Unitário

```python
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_valido(client, evento):
    response = client.post("/api/v1/eventos", json=evento)
    assert response.status_code == 200
    assert response.json()["title"] == evento["title"]
```

---

## 🔐 Testes Futuros com Autenticação

A camada de autenticação está preparada para ser testada com:

* Geração de JWT falso com escopos.
* Testes de rotas protegidas usando `Depends(get_current_user)`.
* Simulação de usuários admin e usuários comuns.

---

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

[⬅ Voltar para o Índice](../README.md)
