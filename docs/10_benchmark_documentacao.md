# 📊 Benchmark de Latência da API – FastTrackAPI

Este documento descreve o processo de benchmark realizado na aplicação **FastTrackAPI — Projeto Prisma**, os resultados obtidos, interpretação dos dados e sugestões para melhoria de desempenho local.

---

## 🎯 Objetivo

Avaliar a **latência de respostas da API local** em ambiente de desenvolvimento, utilizando repositórios em memória e autenticação com token JWT.

---

## ⚙️ Cenário de Execução

- **Modo de execução**: `ENVIRONMENT=test.inmemory`
- **Banco de dados**: repositório em memória (`InMemoryEventoRepo`)
- **Usuário de login**: `alice / secret123`
- **Ferramenta utilizada**: PowerShell (`Invoke-WebRequest`)
- **Requisição avaliada**: `GET /api/v1/eventos`

---

## 📝 Como executar o benchmark

### 1. Permitir execução de scripts no PowerShell (temporariamente)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Rodar o script

Faça o download do arquivo `benchmark.ps1` e execute:

```powershell
.enchmark.ps1
```

O script realiza:

- Login com `alice`
- Obtém um token JWT
- Envia uma requisição autenticada para `/api/v1/eventos`
- Exibe o tempo total da resposta

---

## 📈 Resultado atual

Em execução local com repositório em memória, foi obtido:

```
Status Code: 200
Tempo total: 4132.1205 ms
```

Este tempo representa o intervalo total desde o envio da requisição até o recebimento da resposta da API FastAPI.

---

## ❓ Interpretação

O tempo de **4 segundos** para um endpoint que:
- Executa em memória,
- Sem banco de dados real,
- Sem IO externo,

...é **anormalmente alto**.

---

## 🧪 Investigações realizadas

- 🧪 Com `curl` e `httpx`, o tempo foi de **~60ms**, o que indica que:
  - A API está **respondendo rápido** de fato.
  - O tempo elevado está associado ao **PowerShell** ou ao **logging**.

---

## 🛠️ Ações recomendadas para melhoria

| Item                              | Ação sugerida                          |
|-----------------------------------|----------------------------------------|
| `structlog` com JSON no terminal  | Trocar por `ConsoleRenderer` ou log em arquivo |
| Middleware de logging             | Desativar em ambientes `test` e `inmemory` |
| Terminal do PowerShell            | Usar terminal alternativo (Git Bash, VS Code) |
| `uvicorn --reload`                | Evitar em benchmarks (causa overhead no Windows) |
| Navegador como fonte de latência | Testar com `curl`, `httpx` ou scripts diretos |

---

## 🧩 Conclusão

A latência percebida no navegador ou no PowerShell não representa a performance real da aplicação. O sistema responde rapidamente com `httpx` e `curl`, e está bem estruturado para testes em memória.

---

## 🔗 Arquivo de benchmark

O script PowerShell está disponível como:

- [`benchmark.ps1`](./benchmark.ps1)

---

[⬅ Voltar para o índice](../README.md)
