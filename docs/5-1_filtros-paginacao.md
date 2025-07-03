# Em Construção
# 📌 Filtros e Paginação

Este documento descreve **como** e **por que** o projeto **FastTrackAPI** aplica filtros arbitrários e paginação (`skip` / `limit`) nos dados. A abordagem do projeto segue o padrão **Port-Adapter**: a rota nunca sabe se está falando com RAM ou com o banco — basta trocar o “adaptador” injetado pelo `Depends()`.
Princípio **OCP / port-adapter**. - Ver mais sobre

---

## 🔍 Motivação

* ✅ Desenvolver e testar **rápido**: o adapter em memória roda em milissegundos, sem container de banco.
* ✅ **Contrato estável**: o front-end continua chamando `GET /api/v1/eventos?skip=10&city=Recife`, independe se é na RAM ou em Postgres.
* ✅ **Cobertura de testes** completa já no CI.

---

## 🏗️ Arquitetura

```text
┌──────────┐      provide_event_repo()         ┌─────────────────┐
│ endpoints│ ────────────────────────────────▶ │ EventRepo (⚡) │◀─ SQLAlchemy
└──────────┘                                   │ InMemoryEvent   │◀─ dicionário
                                               └─────────────────┘
```

---

1. **AbstractEventRepo**

```python
class AbstractEventRepo(Protocol):
    def list_partial(self, *, skip:int=0, limit:int=20, **filters) -> list[Event]:
        ...
```

2. **Adapters**

* `InMemoryEventRepo` – filtro + paginação em RAM (dev / testes).
* `SqlEventRepo` (exemplo) – traduz **filters para select() .where(...).offset(skip).limit(limit).

3. **Provider** (`app/deps.py`) escolhe o adapter:

```python
def provide_evento_repo() -> AbstractEventoRepo:
    if settings.environment == "dev":
        return InMemoryEventoRepo()
    return SqlEventoRepo(SessionLocal())
```

---

## ⚙️ Implementação Técnica

1. Filtragem genérica com `**filters` (RAM)

```python
def list_partial(self, *, skip: int = 0, limit: int = 20, **filters) -> list[EventResponse]:
    """
    Devolve um recorte paginado da coleção em memória, aplicando
    dinamicamente filtros recebidos como keyword-args.

    Exemplos de chamada:
        repo.list_partial(skip=0, limit=10)                    # sem filtros
        repo.list_partial(skip=0, limit=10, city="Recife")     # filtra por cidade
        repo.list_partial(skip=0, limit=10, xyz="ABC")         # filtra por outro campo
    """
    data: list[EventResponse] = list(self._db.values())
    
    # aplica cada filtro recebido
    for field, expected in filters.items():
        if expected is None:        # ignora filtros vazios
            continue

        def _match(event: EventResponse) -> bool:
            actual = getattr(event, field, None)
            # comparação "case-insensitive" para strings
            if isinstance(actual, str) and isinstance(expected, str):
                return actual.lower() == expected.lower()
            return actual == expected

        data = [e for e in data if _match(e)]

    # paginação final
    result = data[skip : skip + limit]
    
    logger.info("Listagem parcial de eventos", filtros=filters, total=len(result))
    return result
```

* `_cmp` compara **strings case-insensitive** e mantém igualdade simples para números/datas.
* Nenhum `if city`, `if date_from`, etc.; logo, **novo filtro = zero refator**.
* **skip e limit:** Define qual fatia dos dados será retornada.
* **filters:** Aceita filtros dinâmicos por parâmetros chave-valor.

2. Filtragem via SQLAlchemy

```python
def list_partial(self, skip: int = 0, limit: int = 20, **filters):
    """
    Retorna uma lista paginada de eventos, com filtros dinâmicos aplicáveis
    (ex: `city="Recife"` ou `title="Festival"`).
    Retorna já convertidos para o schema EventResponse.
    """
    query = self.db.query(Event)
    for attr, value in filters.items():
        if value is not None and hasattr(Event, attr):
            query = query.filter(getattr(Event, attr) == value)
    
    db_events = query.offset(skip).limit(limit).all()
    
    return [
        EventResponse.model_validate(e, from_attributes=True)
        for e in db_events
    ]
```

Repare: mesma assinatura, corpo trocado.

---

## 📝 Por que **filters?

Evita “quebrar” o contrato público quando surgirem filtros novos (ex.: date_from, venue_type).

### Contrato de Interface

Todas as implementações futuras (SQLAlchemy, Redis, ElasticSearch, etc.) devem seguir o mesmo contrato (AbstractEventRepo) definido em:

```python
app/repositories/evento.py
```

Exemplo:

```python
def list_partial(self, *, skip: int = 0, limit: int = 20, **filters) -> list[EventResponse]: ...
```

---

## 🌐 Rotas

| Método | Rota                    | Descrição                                             |
| ------ | ----------------------- | ----------------------------------------------------- |
| `GET`  | `/api/v1/eventos`       | lista paginada + filtros (`skip`, `limit`, `city`, …) |
| `GET`  | `/api/v1/eventos/todos` | **obsoleta** – mantida só para retro-compatibilidade  |

Exemplo da chamada HTTP:

```http
GET /api/v1/eventos?skip=10&limit=5&city=Recife
```

A rota encaminha diretamente os parâmetros recebidos para a função `list_partial()`.

```python
@router.get("/eventos", response_model=list[EventResponse])
def listar_eventos(skip: int = 0, limit: int = 20, city: Optional[str] = None):
    return repo.list_partial(skip=skip, limit=limit, city=city)
```

A rota legada /eventos/todos foi removida: listar tudo sem filtro/paginação não é mais suportado.
GET /api/v1/eventos/todos
Mantida apenas para retro-compatibilidade:

---

## ✅ Vantagens da Abordagem

* **Contratos Estáveis:** Adicionar novos filtros não altera o contrato das rotas.
* **Feedback Rápido:** Execução de testes instantânea, pois tudo ocorre na memória.
* **Migração Facilitada:** A transição futura para um banco real é simplificada pelo contrato fixo.
* **Base para Cache:** Facilidade em adicionar cache posteriormente devido ao comportamento determinístico das consultas.
* Facilita benchmark de slice vs cursor	decide-se depois se precisa de paginação baseada em cursor ou token

---

## 🧪 Testes

Os cenários estão em `tests/unit/test_eventos.py`, gerando eventos via
Pydantic e chamando a rota real com o `TestClient`.

```python
def test_paginacao(client, evento_valido):
    # Criar múltiplos eventos
    for i in range(30):
        evento_valido["title"] = f"Evento {i}"
        client.post("/api/v1/eventos", json=evento_valido)

    response = client.get("/api/v1/eventos?skip=10&limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5
```

O mesmo teste passa usando o adapter SQL, bastando setar `ENVIRONMENT=prod` na hora de rodar o CI.

---

## 🚀 Próximos passos

1. **Cursor pagination:** aceitar cursor além de skip/limit.
2. **Filtros avançados:** ranges (date_from/date_to), busca textual, etc.
3. **Cache Redis** para páginas mais pedidas quando em produção.

---

[⬅️ Voltar para o início](../README.md)
