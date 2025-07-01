# 📊🔍 Observabilidade e Logs

Este projeto segue boas práticas de observabilidade, com foco em **registro estruturado de logs**, **diagnóstico de erros** e **rastreabilidade de requisições**. O objetivo é garantir facilidade de manutenção, auditoria e suporte à tomada de decisão em ambientes de produção e desenvolvimento.
Este projeto conta com um sistema estruturado e extensível de logs usando structlog, permitindo registros claros, padronizados e prontos para ferramentas de monitoramento, auditoria e diagnóstico.

---

## 🔊 Configuração do Sistema de Logs

O arquivo `app/core/logging_config.py` define uma configuração completa de logging que pode ser estendida por ambiente.

```python
import logging.config
import sys

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 📊 Níveis de Log Utilizados

| Nível    | Uso recomendado                                  |
| -------- | ------------------------------------------------ |
| DEBUG    | Diagnóstico detalhado em desenvolvimento         |
| INFO     | Registro do funcionamento normal da aplicação    |
| WARNING  | Algo inesperado ocorreu, mas a execução continua |
| ERROR    | Erros que impactam o funcionamento               |
| CRITICAL | Falhas graves (ex: indisponibilidade geral)      |

---

## ✅ Funcionalidades Implementadas

Log estruturado com structlog, no formato JSON.

Middleware de logging que registra todas as requisições HTTP com:

Método (GET, POST, etc.)

Caminho (/api/v1/...)

Código de status da resposta (200, 404, etc.)

Duração da requisição (em segundos)

IP do cliente

Cabeçalho User-Agent

Usuário autenticado (quando houver)

Contexto global por requisição com ContextVar (request_user) para registrar o nome do usuário logado ao longo da requisição.

Filtragem de rotas internas: rotas como /docs, /redoc e /openapi.json são ignoradas nos logs para evitar ruído.

---

## 🧱 Estrutura de Arquivos

Arquivo	Função
app/core/logging_config.py	Configuração do structlog (formato JSON, timestamp, nível de log etc.)
app/core/contextvars.py	Define a variável request_user para guardar o usuário da requisição
app/services/auth_service.py	Define o request_user após autenticação via token
app/middleware/logging_middleware.py	Middleware que registra cada requisição HTTP, incluindo usuário
Diversos mock_*.py, event_mem.py, deps.py	Logs internos de operações simuladas e repositórios

---

## 📰 Exemplo de Uso no Código

```python
import logging
logger = logging.getLogger(__name__)

def criar_evento(evento):
    try:
        logger.info(f"Criando evento: {evento.title}")
        # lógica de criação...
    except Exception as e:
        logger.exception("Erro ao criar evento")
        raise
```

🧩 Exemplo de log gerado
json
Copiar
Editar
{
  "event": "HTTP request log",
  "method": "GET",
  "path": "/api/v1/eventos",
  "status_code": 200,
  "duration": 0.015,
  "client": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "user": "alice",
  "timestamp": "2025-06-15T18:00:00Z",
  "level": "info"
}

---

## 🤖 Logs em Testes e Desenvolvimento

Durante os testes e execuções locais, os logs aparecem no console. Para silenciar ou alterar o nível, pode-se configurar variáveis de ambiente ou sobrescrever a configuração via script.

---

## 🚀 Expansão futura

* Integração com **Sentry** ou **Logstash**.
* Adição de **trace ID** por requisição para correlação de logs.
* Monitoramento por Prometheus + Grafana (exportadores).

🛠 Como estender
Você pode ampliar o sistema de logs com as seguintes práticas:

Logar o tamanho da resposta (bytes).

Registrar os corpos da requisição/resposta (útil para debugging — evite dados sensíveis).

Enviar os logs para ferramentas externas como Loki, ELK (Elasticsearch + Logstash + Kibana) ou DataDog.

Separar logs de erro em arquivos distintos.

Adicionar um ID de correlação por requisição para rastrear logs em microsserviços.

---

## 📌 Dicas

Os logs são estruturados e podem ser consumidos facilmente por ferramentas como Grafana, Prometheus, Loki ou ElasticSearch.

Utilize logger.info(...), logger.warning(...) e logger.error(...) em qualquer ponto do sistema: a estrutura já está preparada para manter os logs padronizados e legíveis.

---

[⬅️ Voltar ao índice](../README.md)
