# Em construção
# 🛣️ Roadmap de Desenvolvimento - FastTrackAPI

Este roadmap apresenta as etapas planejadas e já realizadas para o desenvolvimento da API de eventos **FastTrackAPI**, organizadas por marcos evolutivos, com foco em boas práticas de arquitetura, testes e integrações modernas.

---

## 🔧 Modificações recentes

- Migração da estrutura de armazenamento de lista para `dict` (`eventos_db`)
- Uso de tipos explícitos de retorno nas funções de endpoint
- `location_name` removido da entrada direta do usuário (`EventCreate`)
- `LocalInfo` é gerado com base em API externa; se não houver retorno, salva-se apenas `location_name`

---

## ✅ Concluído

### Etapa 1: Estrutura Inicial do Projeto

* Estrutura de pastas definida por domínio (`schemas/`, `protocols/`, `services/`, `infra/`, `routes/`).
* Utilização de `poetry`, `pytest`, `black`, `mypy` e `isort`.
* Criação do primeiro endpoint `/api/v1/eventos` com CRUD completo em memória.
* Esquemas Pydantic definidos com validações manuais e automáticas.

### Etapa 2: Testes Automatizados

* Separados por `unit` e `integration`.
* Uso de `pytest.mark.parametrize` e `fixtures` reutilizáveis.
* Cobertura aumentada para >85% com relatório HTML.

### Etapa 3: Documentação Detalhada

* Markdown para cada módulo do projeto.
* Cobertura de conceitos como arquitetura, ambiente, dependências e WebSockets.

### Etapa 4: WebSockets e Transmissão

* Suporte a WebSocket para progresso, logs, eventos e upload de arquivos.

---

## 🛠 Em Desenvolvimento

### Etapa 5: Autenticação e Controle de Acesso

* Login com JWT (usuários simulados em `mock_users`).
* Uso de `Depends(get_current_user)` nas rotas.
* Proteção de endpoints sensíveis (ex: `DELETE`).

### Etapa 6: Camadas de Domínio

* Separar responsabilidades em `service/` e `repository/`.
* Definição de interfaces com `Protocol` para inversão de dependência.

### Etapa 7: Integração com Redis

* Cache de `local_info` e `forecast_info`.
* Evitar chamadas externas repetidas.
* TTL configurável.

### Etapa 8: Paginação e Filtros Avançados

* Suporte a query parameters como `limit`, `offset`, `data_inicio`.
* Filtros combinados com busca textual.

### Etapa 9: Integração com Banco de Dados

* Migrar de armazenamento em memória para PostgreSQL.
* Adicionar camada `SQLAlchemy` com repositório adaptado.

### Etapa 10: Pipeline CI/CD

* Automatizar execução de testes e lint com GitHub Actions.
* Deploy automático em ambiente de staging.

### Etapa 11: Benchmark

### Etapa 12: Métricas com Prometheus + Grafana

---

## 🔜 Próximos Passos

### Etapa 11: Modo assíncrono full

* Reescrita de todos os endpoints e serviços em `async def`.

---

## 📅 Planejamento Contínuo

* Adicionar mais testes de erros e cenários inválidos.
* Simulação de carga com `locust` ou `k6`.
* Publicação da API em um registry de demonstração.

---

---

[⬅ Voltar para o Índice](../README.md)
