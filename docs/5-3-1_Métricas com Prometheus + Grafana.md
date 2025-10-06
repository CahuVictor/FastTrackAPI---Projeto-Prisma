# Métricas com Prometheus + Grafana

## O que foi implementado

* Integração da aplicação FastAPI com Prometheus via `prometheus-fastapi-instrumentator`.
* Exposição de métricas HTTP na rota `/metrics`.
* Provisionamento de container Prometheus no `docker-compose`.
* Criação de dashboard Grafana com painéis prontos para requisições, latência e status HTTP.

## Como foi feito

No `main.py`, a instrumentação foi adicionada:

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

## Prometheus

O Prometheus coleta métricas periodicamente da rota `/metrics`. O arquivo `infra/prometheus.yml` define a configuração:

```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

No `docer-compose.yml`

```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infra/prometheus.yml:/etc/prometheus/prometheus.yml
```


## Grafana

Grafana consome os dados do Prometheus e os apresenta em dashboards interativos. Criamos um painel personalizado com:

* Requisições por rota
* Duração média das requisições
* Status HTTP
* Top rotas por volume
* Latência 95% por método

O JSON do dashboard pode ser importado diretamente via interface do Grafana.

No `docer-compose.yml`

```yaml
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

---

## Como testar localmente

### 1. Instalar dependências

```bash
poetry install
poetry add prometheus-fastapi-instrumentator
```

### 2. Iniciar os serviços com Docker

```bash
docker-compose up -d prometheus grafana
```

Certifique-se de que os serviços `prometheus` e `grafana` estão rodando:

* Prometheus: [http://localhost:9090](http://localhost:9090)
* Grafana: [http://localhost:3000](http://localhost:3000)

### 3. Importar o Dashboard

1. Acesse o Grafana
2. Login padrão: `admin` / `admin`
3. Menu lateral → Dashboards → Import
4. Selecione o arquivo [`fastapi_observabilidade_dashboard.json`](docs\examples\fastapi_observabilidade_dashboard.json)
5. Escolha Prometheus como fonte de dados
6. Clique em **Import**

[Referências](docs/9_referencias.md)

### 4. Gerar métricas

Realize requisições para a API (ex: `/api/v1/eventos`) para que métricas sejam registradas.

Acesse:

* [http://localhost:8000/metrics](http://localhost:8000/metrics) para ver as métricas brutas
* [http://localhost:3000](http://localhost:3000) para o dashboard no Grafana

---

## ✅ Passo a Passo: Criar o Dashboard no Grafana

### 1. Acesse o Grafana

* Vá para http://localhost:3000
* Login padrão: admin / admin

### 2. Configure a fonte de dados

* Menu lateral → ⚙️ Administração → Data Sources
* Clique em Add data source
* Selecione Prometheus
* Em URL: http://prometheus:9090
* Clique em Save & test

### 📊 3. Crie um novo Dashboard

* Menu lateral → 📊 Dashboards → New Dashboard
* Clique em Add a new panel

### 🧩 4. Configure os painéis

#### 📌 Painel 1: Requisições por Rota

* Query:
  ```prometheus
  http_server_requests_total
  ```
* Tipo: Time series
* Legend: {{handler}}

#### 📌 Painel 2: Duração Média das Requisições

* Query:
  ```prometheus
  rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])
  ```
* Tipo: Time series
* Unidade: s (segundos)
* Legend: {{handler}}

#### 📌 Painel 3: Códigos de Status HTTP

* Query:
  ```prometheus
  sum by (status) (rate(http_server_requests_total[1m]))
  ```
* Tipo: Bar gauge ou Pie chart
* Legend: {{status}}

#### 📌 Painel 4: Top Rotas por Volume

* Query:
  ```prometheus
  topk(5, sum by (handler) (rate(http_server_requests_total[1m])))
  ```
* Tipo: Bar chart

#### 📌 Painel 5: Latência por Método

* Query:
  ```prometheus
  histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, method))
  ```
* Tipo: Time series
* Unidade: s
* Legend: {{method}}

### 💾 5. Salve o Dashboard

* Clique no ícone 💾 no topo → Dê um nome como “FastAPI - Observabilidade” e salve.

---

## Próximos Passos

* Adicionar Tracing com OpenTelemetry + Jaeger
* Exportar logs para ElasticSearch ou Loki
* Criar alertas no Grafana

---

Essa integração torna o sistema mais transparente e monitorável, permitindo diagnóstico rápido de falhas e análise de performance em tempo real.

---

[⬅️ Voltar ao índice](../README.md)
