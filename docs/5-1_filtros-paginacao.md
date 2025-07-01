# Em Construção
# 📌 Filtros e Paginação in-memory

Este documento descreve como os filtros e a paginação em memória foram implementados no projeto **FastTrackAPI**. Essa abordagem permite rápida prototipagem e facilita testes e desenvolvimento antes da implementação de um banco de dados definitivo, mantendo o mesmo contrato público da API.
Antes de conectar o banco de dados definitivo, usamos um método interno para realizar filtros e paginação diretamente na memória do sistema. Isso permite que as APIs sejam testadas rapidamente sem depender do banco externo.
Princípio **OCP / port-adapter**. - Ver mais sobre

---

## 🔍 Motivação

Antes de conectar ao banco de dados definitivo, é importante garantir que:

* As funcionalidades de paginação (`skip`, `limit`) e filtros de consultas estejam plenamente funcionais.
* Os testes de integração e o front-end possam consumir a API sem alterações adicionais ao trocar a camada de persistência.

Dessa forma, adotou-se uma implementação de filtros e paginação diretamente em memória, simplificando o desenvolvimento inicial.

---

## 📐 Implementação Técnica

### Estrutura em memória

A estrutura utilizada é um repositório em memória definido no arquivo:

```python
app/repositories/event_mem.py
```

A função principal de paginação e filtragem:

```python
def list_partial(self, *, skip: int = 0, limit: int = 20, **filters):
    data = list(self._events.values())
    for key, expected in filters.items():
        if expected is not None:
            data = [item for item in data if getattr(item, key, None) == expected]
    return data[skip: skip + limit]
```

* **skip e limit:** Define qual fatia dos dados será retornada.
* **filters:** Aceita filtros dinâmicos por parâmetros chave-valor.

📝 Por que **filters?

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

## 🛣️ Rotas Implementadas

### GET `/api/v1/eventos`

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

Testes cobrindo paginação e filtragem são implementados no arquivo:

```python
tests/unit/test_eventos.py
```

Exemplo de um teste:

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

Esses testes garantem que a funcionalidade está correta e pode ser expandida sem quebrar contratos.

**filters percorrido dinamicamente	Escalável: novos filtros (ex. date_from) não exigem refactor de assinatura nem de testes.
Comparação “case-insensitive” só para str	Evita falso-negativo em campos textuais sem afetar tipos numéricos/datas.
expected is None → filtro é ignorado	Permite passar o parâmetro sempre, sem precisar de condicionais na rota (`city: str
Docstring com exemplos	Facilita entendimento para quem implementar o próximo adapter (SQL, Elastic etc.).

— e, quando você quiser acrescentar outro parâmetro (date_from, venue_type…), basta incluí-lo no Query(...) da rota e repassar para list_partial sem alterar o contrato nem quebrar clientes.

## Próximos passos possíveis

Cursor Pagination: manter skip/limit para retro-compatibilidade e aceitar um cursor para coleções muito grandes.

---

migrations

2. Recrie a migração corretamente
Como a migração anterior não criou a tabela events, você precisa apagar essa versão e gerar outra:

bash
Copiar
Editar
# 1. Apague o migration antigo (ou renomeie para backup)
rm migrations/versions/*.py  # cuidado: isso remove TODAS as versões de migração

# 2. Gere nova migração com os modelos agora corretamente importados
alembic revision --autogenerate -m "create tables"

# 3. Aplique a nova migração
alembic upgrade head

Esse erro aconteceu porque você deletou ou removeu os arquivos da pasta migrations/versions/, mas o banco de dados ainda está com o controle interno apontando para a versão 'e69fdb78a658'.

✅ Como resolver isso corretamente
📌 Objetivo:
Resetar o histórico de migrações para sincronizar o banco com a nova estrutura de arquivos.

✅ Etapas para resolver:
1. Apague a tabela de controle de migração (alembic_version)
Essa tabela fica no seu banco de dados e guarda qual versão está atualmente aplicada. Execute no seu banco (via psql, DBeaver, pgAdmin, ou terminal):

sql
Copiar
Editar
DROP TABLE alembic_version;
Isso permite que o Alembic recrie o controle corretamente com a nova versão.

2. Crie uma nova migração do zero
Com os modelos devidamente importados no migrations/env.py, rode:

bash
Copiar
Editar
alembic revision --autogenerate -m "create all tables"
Isso vai gerar um novo arquivo de migração em migrations/versions/.

3. Aplique essa nova migração ao banco
bash
Copiar
Editar
alembic upgrade head
Se tudo estiver correto, agora a tabela events e as outras (local_infos, forecast_infos) serão criadas.

Entendendo o comando alembic upgrade head
O comando:

bash
Copiar
Editar
alembic upgrade head
é utilizado para aplicar migrações de banco de dados geradas por meio da ferramenta Alembic.

O Alembic é uma ferramenta do ecossistema SQLAlchemy utilizada para:

Gerenciar evoluções/migrações no esquema do banco (criação, alteração ou exclusão de tabelas e campos).

Garantir que seu banco tenha sempre um esquema consistente com os modelos definidos na aplicação Python.

📌 Como o Alembic sabe qual banco usar?
O Alembic procura sua configuração de banco no arquivo chamado alembic.ini (que fica na raiz do seu projeto ou onde você executa o comando). Nele há uma linha que define a conexão com o banco:

Exemplo (alembic.ini):

ini
Copiar
Editar
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://prisma:prisma123@localhost:5432/prisma_db
Aqui:

postgresql://prisma:prisma123@localhost:5432/prisma_db define exatamente:

user: prisma

senha: prisma123

host: localhost

porta: 5432

nome do banco: prisma_db

Essa é a conexão usada pelo comando alembic upgrade head.

🗃️ Se eu tiver mais de um banco, como o Alembic saberia qual usar?
O Alembic usa exatamente o banco especificado no alembic.ini. Se você tiver múltiplos bancos, você precisará ter:

Múltiplos arquivos de configuração (alembic.ini) separados por banco, ou

Ajustar dinamicamente a URL via variáveis de ambiente ou scripts antes de executar alembic.

Exemplo com variável de ambiente no alembic.ini:

ini
Copiar
Editar
sqlalchemy.url = ${DATABASE_URL}
Você pode definir no terminal antes de rodar o comando:

bash
Copiar
Editar
export DATABASE_URL=postgresql://prisma:prisma123@localhost:5432/prisma_db
alembic upgrade head
Ou pode ter múltiplos arquivos alembic.ini (por exemplo alembic-db1.ini, alembic-db2.ini) e chamar explicitamente:

bash
Copiar
Editar
alembic -c alembic-db1.ini upgrade head
alembic -c alembic-db2.ini upgrade head

---

[⬅️ Voltar para o início](../README.md)
