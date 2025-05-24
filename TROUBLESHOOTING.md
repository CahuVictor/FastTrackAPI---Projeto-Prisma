# FastTrackAPI – Guia de *Troubleshooting*

Este guia rápido reúne **sintomas recorrentes**, *checklists* de diagnóstico e **soluções testadas** para problemas que costumam travar o servidor FastAPI/Uvicorn em desenvolvimento.

> **Como usar** : quando algo "não sobe" ou o `/docs` fica carregando, siga a ordem → **Checklist inicial → Sintoma específico → Receita de correção**.

---

## ☑️ Checklist inicial

1. **Servidor está de pé?**

   ```powershell
   netstat -ano | findstr :8000  # ou porta escolhida
   ```
2. **Porta livre?** Se houver PID, mate-o:

   ```powershell
   taskkill /PID <pid> /F
   ```
3. **Abrir OpenAPI direto** – evita o Swagger‑UI:

   ```powershell
   curl.exe -I http://127.0.0.1:8000/openapi.json
   ```
4. **Rodar sem reload** – isola bugs do *watcher*:

   ```powershell
   uvicorn app.main:app --port 8000 --log-level debug
   ```
5. **Rodar com log de acesso** – :

   ```powershell
   uvicorn app.main:app --reload --log-level debug --acess-log
   ```
---

## 1 – Swagger UI não carrega (spinner infinito)

| Indicador                               | Causa provável           | Diagnóstico                                                               | Solução rápida                                                  |
| --------------------------------------- | ------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `/openapi.json` **500** ou sem resposta | Erro ao gerar schema     | `uvicorn --log-level debug` → traceback                                   | ➜ Corrija modelo Pydantic ou `custom_openapi()`. Detalhes § 1.1 |
| `/openapi.json` **200** mas UI branca   | CDN do Swagger bloqueado | `curl /openapi.json` OK, DevTools→Network falha em `swagger-ui-bundle.js` | ➜ Baixe assets localmente ou use ReDoc                          |
| Navegador fica offline                  | Proxy/firewall           | Teste no cURL fora do proxy                                               | ➜ Configurar proxy ou VPN                                       |

\### 1.1 Erros típicos de schema

| Traceback final                           | Causa                                                               | Ajuste                                               |
| ----------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------- |
| `ValueError: Duplicate operation ID`      | Path fixo depois de dinâmico (`/items/{id}` antes de `/items/novo`) | Reordenar rotas ou definir `operation_id` único      |
| `RecursionError: maximum recursion depth` | Modelos com referência circular                                     | Usar `update_forward_refs()` ou quebrar modelos      |
| `TypeError: Object of type datetime…`     | `json_schema_extra` com tipos não‑serializáveis                     | Converter para *str* / números simples               |
| Conexão sem resposta, sem traceback       | *orjson* bug em Windows/Py 3.12 (< 3.10.3)                          | `poetry add orjson@latest` ou `poetry remove orjson` |

---

## 2 – Porta 8000 já em uso / WinError 10048

**Sintoma**: "Normally only one usage of each socket…" logo ao iniciar.

**Diagnóstico**
`netstat -ano | findstr :8000` mostra PID(s) **LISTENING** / **CLOSE\_WAIT**.

**Correção**

```powershell
# mata processos órfãos
for %i in (<pid1> <pid2>) do taskkill /PID %i /F
```

Ou iniciar em outra porta: `uvicorn app.main:app --port 8001`.

---

## 3 – Auto‑reload reinicia em loop e derruba server

### 3.1 *watchfiles* bug (Windows + Unicode path)

* **Sintoma** : log mostra `Application startup complete` seguido de `Shutting down` em segundos.
* **Fix** : `poetry add "watchfiles>=0.21.0"` ou usar reloader antigo:
  `uvicorn … --reload-impl watchgod`.
* **Dica** : evite caminhos com acentos/espaço (ex. `C:\dev\fasttrackapi`).

### 3.2 Arquivos *pyc* tocados por antivírus/VS Code

* Limite a pasta monitorada:
  `uvicorn … --reload --reload-dir app --reload-exclude **/*.pyc`.

---

## 4 – Dicas de prevenção

1. **Tenha sempre um script** `debug_schema.py`:

   ```python
   from fastapi.openapi.utils import get_openapi
   from app.main import app
   print(len(get_openapi(title=app.title, version=app.version, routes=app.routes)))
   ```
2. **Cacheie** seu `custom_openapi()` usando `app.openapi_schema`.
3. **Organize rotas**: estáticas antes de dinâmicas; nomes de handler únicos.
4. **Automatize** atualização de libs críticas: `orjson` e `watchfiles`.
5. **Documente** quaisquer flags especiais (`--reload-impl`, proxies etc.).

---

## 5 – Referências úteis

* FastAPI Docs – [Deployment Concepts](https://fastapi.tiangolo.com/deployment/)
* Uvicorn – [Settings & CLI](https://www.uvicorn.org/settings/)
* Microsoft – [WinError 10048](https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2)
* Watchfiles changelog – *Fix Unicode path loop* (0.21.0)

> **ProTip** : Renomeie este arquivo para **`TROUBLESHOOTING.md`** e mantenha no repositório raiz – editores (GitHub, VS Code) reconhecem o padrão e mostram link automático na interface.

---

### Histórico de revisões

| Data       | Alteração      | Autor                |
| ---------- | -------------- | -------------------- |
| 2025‑05‑23 | Versão inicial | ChatGPT (assistente) |
