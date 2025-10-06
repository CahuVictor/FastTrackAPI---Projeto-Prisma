
# 🌤️ Atualização Automática da Previsão do Tempo via BackgroundTasks

## ✅ Visão Geral

Esta funcionalidade introduz uma **atualização assíncrona e não bloqueante** da previsão do tempo dos eventos, utilizando o recurso `BackgroundTasks` do FastAPI. Agora, toda vez que um evento é consultado via `GET /events/{id}`, o sistema verifica se a previsão está desatualizada e a atualiza automaticamente em segundo plano — sem impactar a experiência do usuário.

---

## 🚀 Por que isso é importante

### 🔄 Dados sempre atualizados
O sistema garante que a previsão do tempo seja atualizada **automaticamente** sempre que estiver ausente ou com mais de 24 horas de desatualização.

### ⚡ Respostas rápidas
A atualização acontece **em segundo plano**, ou seja, o usuário recebe a resposta da API imediatamente enquanto a atualização é feita de forma assíncrona.

### 🧪 Testável com mocks
Em ambientes de testes (`test.inmemory`), é possível simular o comportamento da funcionalidade sem chamar serviços externos reais.

### 🧱 Atualização incremental e segura
Somente o campo aninhado `forecast_info` é modificado — o restante dos dados do evento permanece intacto.

---

## 🔍 Componentes principais

### ✅ Endpoint `get_event_by_id`

```python
if should_update_forecast(event.forecast_info):
    background_tasks.add_task(
        atualizar_forecast_em_background,
        event_id
    )
```

Sempre que um evento é consultado:
1. Verifica se a previsão do tempo está ausente ou desatualizada.
2. Se necessário, adiciona uma tarefa de atualização em segundo plano.
3. A resposta é retornada imediatamente ao usuário.

---

### ⚙️ Lógica do background

```python
async def atualizar_forecast_em_background(event_id: int):
    ...
    forecast = service.get_by_city_and_datetime(event.city, event.event_date)
    update = ForecastInfoUpdate.model_validate(data)
    update_event(event, update, attr="forecast_info")
    repo.replace_by_id(event_id, event)
```

O processo:
- Busca a previsão com base na cidade e data do evento.
- Valida os dados e registra o timestamp de atualização (`updated_at`).
- Atualiza apenas o campo `forecast_info` do evento.

---

### 🧠 Quando atualizar a previsão

```python
def should_update_forecast(forecast_info):
    return forecast_info is None or (datetime.now() - forecast_info.updated_at > timedelta(days=1))
```

Garante que a previsão só seja atualizada quando necessário, reduzindo consumo de recursos.

---

### 🛠️ Utilitário de atualização parcial

- `update_event_forecast`: mescla os dados da nova previsão com os já existentes.
- `update_event`: aplica atualizações seguras tanto nos campos principais quanto nos campos aninhados (como `local_info` e `forecast_info`).
- Usa o Pydantic para validação de integridade dos dados.

---

## 📁 Arquivos e Módulos Envolvidos

- `app/api/v1/endpoints/events.py`: integração do `BackgroundTasks`.
- `app/deps.py`: fornece dependências mockadas ou reais conforme ambiente.
- `app/repositories/`: suporte à substituição parcial de eventos.
- `app/schemas/`: adição do campo `updated_at` em `ForecastInfoUpdate`.
- `app/services/forecast.py`: lógica de atualização assíncrona.
- `app/utils/patch.py`: utilitários para atualização segura dos dados do evento.

---

## 🧪 Como testar

1. Defina `forecast_info` como `None` ou com `updated_at` antigo.
2. Faça uma chamada `GET /events/{id}`.
3. Verifique:
   - A resposta vem imediatamente.
   - O campo `forecast_info.updated_at` é atualizado em segundo plano.
   - Os logs indicam a tentativa e o resultado da atualização.

---

## ✅ Benefícios Resumidos

| Funcionalidade                          | Vantagem                                    |
|----------------------------------------|---------------------------------------------|
| ✅ Atualização assíncrona               | Respostas rápidas ao usuário                |
| ✅ Lógica inteligente de atualização    | Evita chamadas e gravações desnecessárias   |
| ✅ Validação de dados com Pydantic      | Mais segurança e integridade                |
| ✅ Design modular e reutilizável        | Fácil de manter e expandir                  |
| ✅ Ambientes isolados com mocks         | Testes confiáveis e controlados             |

---

[⬅️ Voltar para Tecnologias & Boas Práticas](../5_tecnologias-boas-praticas.md)