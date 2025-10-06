# 🌐 URLs Dinâmicas e Configuração Externa

Para maximizar a flexibilidade e evitar a necessidade de novos deploys a cada mudança de rota de APIs externas, o projeto adota uma estratégia de **resolução dinâmica de URLs**.

## 🧠 Lógica de Resolução

A função `get_service_url(service_name: str)` no módulo `app.utils.service_url` busca a URL do serviço seguindo a seguinte ordem de prioridade:

1. **Arquivo `runtime_urls.json`**  
   → Permite que o sistema continue funcionando mesmo que a URL original mude em tempo de execução.

2. **Variáveis de ambiente (.env)**  
   → Fallback seguro, lido uma única vez na inicialização da aplicação (`Config.SERVICE_NAME_URL`).

3. **Erro 500 se ausente**  
   → Caso nenhuma das opções esteja presente, o sistema gera um erro interno com log informando o serviço ausente.

---

## 📁 Exemplo do `runtime_urls.json`

```json
{
  "forecast_info": "https://api.nova-previsao.com",
  "local_info": "https://dados.cidades.gov/api"
}
```

Este arquivo pode ser criado ou atualizado automaticamente pela API de administração `/admin/urls`.

---

## 🛠️ Rota de Administração

**PATCH /admin/urls**  
Permite atualizar endpoints externos dinamicamente, persistindo as alterações em `runtime_urls.json`.

### Corpo da requisição:

```json
{
  "forecast_info": "https://api.custom.com",
  "local_info": "https://outro-servidor.com"
}
```

### Exemplo de resposta:

```json
{
  "forecast_info": "https://api.custom.com",
  "local_info": "https://outro-servidor.com"
}
```

---

## ✅ Benefícios

- Nenhum redeploy é necessário para alterar rotas externas.
- Ideal para ambientes com IPs dinâmicos, testes A/B ou fallback de serviços.
- Facilita testes locais com mocks alternativos.

---

## 🔐 Segurança e Cuidados

- A rota `/admin/urls` **deve ser autenticada** e acessível apenas a usuários com papel `admin`.
- Em produção, **não exponha esse endpoint sem validação de permissões**.

---

## 🧪 Comportamento em Testes

Durante os testes, é possível mockar `get_service_url` para retornar URLs específicas conforme desejado, garantindo controle sobre os testes sem dependência do `.env` ou do arquivo JSON.

---

[⬅️ Voltar para o início](../README.md)
