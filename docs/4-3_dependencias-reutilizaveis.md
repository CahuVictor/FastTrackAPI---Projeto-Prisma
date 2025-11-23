# 🔄 Dependências Reutilizáveis e Testáveis

O projeto **FastTrackAPI** utiliza uma abordagem de **injeção de dependências com contratos (Protocol)** para tornar o código modular, testável, fácil de manter e expansível sem alterações profundas no código dos endpoints.

---

## 📌 O que foi Implementado

1. **Contratos Definidos (`Protocol`)** para os principais serviços da aplicação:

   * Usuários (`AbstractUserRepo`) → `app/services/interfaces/user_protocol.py`
   * Eventos (`AbstractEventoRepo`) → `app/repositories/evento.py`
   * Previsão do tempo (`AbstractForecastService`) → `app/services/interfaces/forecast_info_protocol.py`
   * Informações locais (`AbstractLocalInfoService`) → `app/services/interfaces/local_info_protocol.py`

2. **Implementações Mockáveis**:

   * `MockUserRepo` → `app/services/mock_users.py`
   * `MockForecastService` → `app/services/mock_forecast_info.py`
   * `MockLocalInfoService` → `app/services/mock_local_info.py`
   * `InMemoryEventoRepo` (e `SQLEventRepo`) → `app/repositories/evento_mem.py` e `app/repositories/event_orm_db.py`

3. **Providers únicos** registrados em `app/deps.py`, usados nos endpoints com `Depends(...)`, permitindo substituição fácil entre implementações mockadas e reais:

   * `provide_user_repo`
   * `provide_forecast_service`
   * `provide_local_info_service`
   * `provide_event_repo`

4. **Endpoints Refatorados** para utilizar dependências via `Depends(...)`, eliminando acoplamento com implementações específicas:

   * Login → `app/api/v1/endpoints/auth.py`
   * Rotas de eventos → `app/api/v1/endpoints/eventos.py`



---

## 🛠️ Estrutura dos Protocolos

Cada serviço tem um protocolo definido explicitamente que determina suas operações disponíveis:

**Exemplo de protocolo para repositório de eventos:**

```python
# app/repositories/evento.py
from typing import Protocol
from app.schemas.event.event_create import EventCreate, EventResponse

class AbstractEventRepo(Protocol):
    def list_all(self) -> list[EventResponse]: ...
    def get(self, evento_id: int) -> EventResponse | None: ...
    def add(self, evento: EventCreate) -> EventResponse: ...
    def replace_all(self, eventos: list[EventResponse]) -> list[EventResponse]: ...
    def replace_by_id(self, evento_id: int, evento: EventResponse) -> EventResponse: ...
    def delete_all(self) -> None: ...
    def delete_by_id(self, evento_id: int) -> bool: ...
    def update(self, evento_id: int, data: dict) -> EventResponse: ...
```

---

## 🧩 Implementações Mockadas

As implementações mockadas são utilizadas para testes rápidos e independentes, garantindo confiabilidade sem depender de recursos externos ou complexos.
As implementações mockadas são utilizadas para testes rápidos e independentes, garantindo confiabilidade sem depender de recursos externos.

**Exemplo de uso de implementação mock:**

```python
# app/services/mock_local_info.py
from app.services.interfaces.local_info import AbstractLocalInfoService

class MockLocalInfoService(AbstractLocalInfoService):
    async def get_by_name(self, location_name: str):
        return {
            "location_name": location_name,
            "capacity": 300,
            "venue_type": "Auditório",
            "is_accessible": True,
            "address": "Rua Exemplo, 123",
            "past_events": []
        }
```

---

## 🔍 Benefícios da Abordagem

* **Facilidade em Testes:** Substituição fácil por mocks durante testes unitários e de integração.
* **Baixo Acoplamento:** Camadas dependem apenas de contratos claros.
* **Flexibilidade:** Troca de implementação sem mudanças significativas na lógica de negócio.
* **Conformidade com o Princípio SOLID:** Alta coesão, baixo acoplamento, e código extensível com segurança.

---

## ✅ O que pode ser Testado

Com dependências injetáveis, é possível testar isoladamente:

* Autenticação de usuários (`MockUserRepo`)
* Operações CRUD em eventos (`InMemoryEventoRepo` ou `SQLEventRepo`)
* Integração com APIs externas como previsão do tempo (`MockForecastService`)
* Integração com APIs externas de informações locais (`MockLocalInfoService`)
* Cenários diversos de permissões e acessos (admin, editor, viewer)

---

> 📁 Referências no Código:
>
> * Contratos: `app/services/interfaces/`, `app/repositories/evento.py`
> * Mocks: `app/services/mock_*.py`, `app/repositories/evento_mem.py`
> * Injeção: `app/deps.py`
> * Uso real nos endpoints: `app/api/v1/endpoints/auth.py`, `eventos.py`

---

[⬅️ Voltar para o início](../README.md)
