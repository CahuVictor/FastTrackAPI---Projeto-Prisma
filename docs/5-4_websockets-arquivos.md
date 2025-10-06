# 🔌 WebSockets e Transmissão de Arquivos

O projeto **FastTrackAPI** inclui funcionalidades em tempo real utilizando WebSockets e transmissão assíncrona de arquivos para garantir melhor interação com usuários, painéis e sistemas externos.
Esta seção descreve como foram implementadas as funcionalidades relacionadas a tempo real e manipulação de arquivos no projeto, detalhando o uso de WebSockets e rotas para upload e download de arquivos.
O WebSocket permite uma comunicação interativa e em tempo real entre o servidor e os clientes conectados, possibilitando notificações instantâneas, progresso em tempo real e atualizações de dashboards.

---

## 📡 Funcionalidades com WebSockets

A API permite abrir canais de comunicação persistente com clientes via WebSockets para:

* Receber eventos com barra de progresso em tempo real.
* Atualizar dashboards com contagens ao vivo.
* Monitorar logs enquanto tarefas estão em execução.
* Detectar usuários online.
* Notificar atualizações de novos eventos imediatamente.

### Exemplo de Rota WebSocket

```python
@router.websocket("/ws/eventos/progresso")
async def progresso_eventos(ws: WebSocket):
    await ws.accept()
    for i in range(10):
        await ws.send_json({"progresso": i * 10})
        await asyncio.sleep(1)
    await ws.close()
```

* **Upload de Eventos em Tempo Real:**

  * Notificações de progresso linha a linha durante o upload.
  * Indicação imediata de erros por linha.
  * Mensagem final ao término da importação.

* **Dashboard ao Vivo:**

  * Contagem de eventos atualizada automaticamente sem necessidade de polling HTTP.
  * Número de usuários conectados atualizado em tempo real.

* **Logs e Status de Tarefas Longas:**

  * Envio contínuo de logs ou mensagens de status enquanto tarefas são executadas.

* **Notificações Administrativas:**

  * Avisos aos administradores sempre que novos eventos forem criados ou houver alterações massivas.

---

## 📁 Upload de Arquivos com Progresso

A API permite upload de arquivos de forma segura e compatível com acompanhamento de progresso.
Implementado um endpoint `/eventos/upload` para permitir o upload de arquivos CSV contendo múltiplos eventos. Cada linha do CSV representa um evento completo que será processado e adicionado ao repositório.

### Como funciona:

* O cliente abre uma conexão WebSocket para escutar o progresso.
* Envia o arquivo via HTTP (com multipart).
* A API publica atualizações de progresso para o canal correspondente.

### Exemplo de Integração (Pseudocódigo):

```javascript
// WebSocket para escutar progresso
const ws = new WebSocket("ws://localhost:8000/ws/upload/arquivo1")
ws.onmessage = (msg) => console.log("Progresso:", msg.data)

// Upload HTTP separado
fetch("/api/v1/uploads", {
  method: "POST",
  body: formData,
})
```

* Formato esperado do CSV:

```csv
title,description,event_date,city,participants,local_info
Evento 1,Descrição do evento,2025-07-01T10:00:00,Recife,Alice;Bob,"{\"location_name\": \"Auditório Central\", \"capacity\": 300, \"venue_type\": \"Auditório\", \"is_accessible\": true, \"address\": \"Rua Exemplo, 123\", \"past_events\": [], \"manually_edited\": false}"
```

* Durante o upload:

  * Validação das linhas do arquivo.
  * Retorno detalhado via WebSocket sobre o status e possíveis erros.

## 📁 Download de Eventos em JSON

Foi criado um endpoint `/eventos/download` que permite baixar os eventos existentes no repositório em formato JSON.

* Exemplo do endpoint:

```http
GET /api/v1/eventos/download
```

* A resposta será um arquivo JSON contendo todos os eventos cadastrados:

```json
[
  {
    "title": "Evento 1",
    "description": "Descrição do evento",
    "event_date": "2025-07-01T10:00:00",
    "city": "Recife",
    "participants": ["Alice", "Bob"],
    "local_info": {
      "location_name": "Auditório Central",
      "capacity": 300,
      "venue_type": "Auditório",
      "is_accessible": true,
      "address": "Rua Exemplo, 123",
      "past_events": [],
      "manually_edited": false
    }
  }
  // Mais eventos...
]
```

---

## 📤 Transmissão de Logs de Processamento

Durante tarefas demoradas (ex: análise de eventos), logs são enviados em tempo real:

* Evita polling.
* Melhora a transparência de operações.
* Pode ser conectado a interfaces com suporte a console.

---

## 🔄 Atualizações em Tempo Real

Eventos criados, atualizados ou deletados podem ser notificados a clientes automaticamente:

* Web frontend recebe mensagem e atualiza UI.
* Integração com outras APIs que se inscrevem por WebSocket.

---

## 🧪 Testes e Simulações

As funcionalidades de WebSocket são testadas com:

* Testes unitários usando `asyncclient` e `lifespan`.
* Simulação de conexões simultâneas.
* Interação com frontend via ferramentas como Postman, websocat e browsers.

---

[⬅ Voltar para o índice](../README.md)
