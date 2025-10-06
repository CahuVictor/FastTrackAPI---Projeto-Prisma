# ⚡️ Latência em Mocks: o caso do `MockUserRepo`

> *Categoria: Tecnologias & Boas Práticas*

---

## Problema identificado

Durante o uso do \`\` cada requisição HTTP instanciava **novamente** o repositório de usuários em memória. No construtor (`__init__`) eram executadas chamadas custosas a `get_password_hash()` para **todas** as senhas do mock (*bcrypt* por padrão). Isso acrescentava **3 – 10 s** de latência por request, mesmo quando o endpoint apenas precisava ler um usuário.

```python
class MockUserRepo(AbstractUserRepo):
    def __init__(self):
        _RAW_USERS = [...]
        self._users = {
            username: UserInDB(
                username=username,
                hashed_password=get_password_hash(raw_pwd),  # ❌ custoso
                ...
            )
            for username, raw_pwd, ... in _RAW_USERS
        }
```

## Causa-raiz

1. **Instanciação por request** – Cada rota dependia de `provide_user_repo()` que retornava `MockUserRepo()` sempre.
2. **Operação pesada** – `get_password_hash()` faz PBKDF2/Bcrypt (\~80–120 ms cada).
3. **Repetição desnecessária** – A lista *mock* não muda em tempo de execução.

## Solução adotada

1. **Singleton em memória** para o repositório de usuários quando o *environment* é `test.inmemory`.

```python
# app/deps_singletons.py
from app.repositories.user_mem import InMemoryUserRepo
_in_memory_user_repo_instance: InMemoryUserRepo | None = None

def get_in_memory_user_repo() -> InMemoryUserRepo:
    global _in_memory_user_repo_instance
    if _in_memory_user_repo_instance is None:
        _in_memory_user_repo_instance = InMemoryUserRepo()  # ✅ custo pago 1×
    return _in_memory_user_repo_instance
```

2. **Provider adaptativo** que injeta o singleton apenas em ambiente de teste.

```python
# app/deps.py
from app.deps_singletons import get_in_memory_user_repo

def provide_user_repo(db: Session = Depends(get_db)) -> AbstractUserRepo:
    if settings.environment == "test.inmemory":
        return get_in_memory_user_repo()  # 🔄 sempre a mesma instância
    return UserRepo(db)  # produção/integração
```

## Boas práticas para evitar esse problema

| Prática                         | Descrição                                            | Quando aplicar                        |
| ------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| **Instância única (singleton)** | Crie o objeto pesado uma vez e reutilize             | Mocks, caches, repositórios in‑memory |
| **Lazy Loading**                | Inicialize partes custosas somente no 1º uso         | APIs de terceiros, objetos grandes    |
| **Separar fase de carga**       | Faça pré‑processamento na startup (evento `startup`) | Seeds de banco, dicionários estáticos |
| **Benchmarks**                  | Meça tempo de construção vs. requisição              | Antes de mover para produção          |
| **Ambiente‑aware providers**    | Adapte `Deps` conforme `settings.environment`        | test/dev vs. prod                     |

## Checklist para mocks performáticos

*

## Resultado

Após a mudança, o tempo médio das rotas caiu de **≈ 4,2 s** para **≈ 30 ms** em ambiente `test.inmemory`, eliminando gargalo de latência sem afetar rotas de produção.

---

[⬅️ Voltar para Tecnologias & Boas Práticas](../5_tecnologias-boas-praticas.md)
