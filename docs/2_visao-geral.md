### Visão Geral

A aplicação permite que usuários criem e visualizem eventos. Cada evento pode conter informações como título, descrição, data e local. Além disso, a aplicação enriquece os dados do evento com informações obtidas de fontes externas:

1. **Banco de Dados Interno (PostgreSQL):**  
   Armazena todas as informações principais dos eventos, como título, descrição, data, local e participantes.

2. **Banco de Dados Externo Simulado (API controlada):**  
   Representa um sistema externo com dados complementares, como a capacidade de locais ou histórico de eventos em determinado espaço. Esse banco será acessado via uma API REST criada especificamente para simular esse comportamento.

3. **API Pública (OpenWeatherMap):**  
   Fornece previsões do tempo baseadas na data e local do evento, integrando dados do mundo real à aplicação.

### Exemplo de Fluxo

- O usuário cria um evento pelo backend.
- A aplicação:
  - Armazena os dados no banco de dados interno.
  - Consulta a API simulada para informações do local.
  - Consulta a API pública para obter a previsão do tempo.
- Os dados combinados são exibidos ao usuário final.

---

[⬅️ Voltar para o início](../README.md)
