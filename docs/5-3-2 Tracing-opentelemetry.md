# Tracing com OpenTelemetry + Jaeger

## Visão Geral

O tracing distribuído permite acompanhar o fluxo de uma requisição através dos serviços da aplicação, medindo a latência e identificando gargalos com precisão. Nesta seção documentamos a implementação do tracing com OpenTelemetry e visualização através do Jaeger.

---

## Ferramentas Utilizadas

* [OpenTelemetry](https://opentelemetry.io/) (API + SDK)
* [Jaeger](https://www.jaegertracing.io/) para visualização
* `opentelemetry-instrumentation-fastapi` para integração automática

---

## Como foi implementado

### 1. Instalação das dependências

```bash
poetry add \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-jaeger \
  opentelemetry-instrumentation-fastapi
```

### 2. Modularização da configuração

Foi criado o arquivo `app/core/tracing_config.py`:

```python
# app/core/tracing_config.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def configure_tracing(agent_host: str = "localhost", agent_port: int = 6831):
    trace.set_tracer_provider(TracerProvider())

    jaeger_exporter = JaegerExporter(
        agent_host_name=agent_host,
        agent_port=agent_port,
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
```

### 3. Instrumentação no `main.py`

```python
from app.core.tracing_config import configure_tracing
configure_tracing(agent_host="jaeger")  # ou "jaeger" se estiver no docker-compose

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

### 4. Docker Compose

Adicionamos o serviço Jaeger:

```yaml
  jaeger:
    image: jaegertracing/all-in-one:1.52
    ports:
      - "6831:6831/udp"
      - "16686:16686"
```

A interface do Jaeger ficará disponível em [http://localhost:16686](http://localhost:16686)

---

## Como testar localmente

1. Inicie os containers:

```bash
docker-compose up -d jaeger
```

2. Realize chamadas na API, como:

```
curl http://localhost:8000/api/v1/eventos
```

3. Acesse o painel Jaeger: [http://localhost:16686](http://localhost:16686)

4. Selecione o serviço (ex: "fastapi") e clique em "Find Traces"

5. Explore os spans e visualize o tempo de cada etapa

---

## Próximos Passos

* Adicionar contextos personalizados e spans manuais em operações importantes (ex: busca, parsing, integrações)
* Exportar traces via OTLP para observabilidade centralizada
* Integrar com logs estruturados (Log + TraceID)

---

Com a integração do OpenTelemetry, o projeto passa a ter visibilidade de ponta a ponta das requisições, identificando gargalos e possibilitando análise de performance distribuída.

---

[⬅️ Voltar ao índice](../README.md)
