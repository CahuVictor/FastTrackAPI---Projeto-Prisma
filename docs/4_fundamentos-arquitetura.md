# 🧱 Fundamentos de Arquitetura

Esta seção reúne os pilares estruturais do projeto FastTrackAPI, documentando as principais decisões arquiteturais que sustentam a organização do código, a separação de responsabilidades, a segurança por configuração e a capacidade de testar componentes de forma isolada.

Cada tópico descrito abaixo possui um documento complementar com exemplos práticos e código.

## 📐 Arquitetura do Projeto
Aborda a organização em camadas da aplicação:

* **Router**: camadas de entrada da API, definidas com FastAPI.
* **Service**: onde vive a lógica de negócio e validações adicionais.
* **Repository**: abstração da persistência de dados, atual ou futura.
* **Schemas**: definem os contratos de entrada e saída usando Pydantic.
* **Modelos de dados**: futuros modelos ORM para bancos relacionais.
* **Mocks**: usados para simular integrações externas (clima, localização).

O objetivo é garantir separação de responsabilidades, reutilização e facilidade de teste.

## ⚙️ Configuração por Ambiente + Fallback Seguro
Explica como o projeto se adapta automaticamente a diferentes contextos (dev, test, prod) utilizando:

* Variáveis .env específicas por ambiente.
* Validação automática com pydantic.BaseSettings.
* Defaults seguros para fallback automático.
* Permite rodar a aplicação sem dor em diferentes ambientes, incluindo testes e deploy.

Inclui instruções para definir variáveis obrigatórias e como evitamos execução em ambientes mal configurados.

## ♻️ Dependências Reutilizáveis e Testáveis
Demonstra como o uso de Protocolos (PEP 544) e injeção de dependências com Depends permite:

* Trocar implementações reais por mocks em testes com facilidade.
* Isolar camadas sem acoplamento rígido.
* Reaproveitar contratos (interfaces) entre repositórios, serviços e controladores.

Essa abordagem fortalece a manutenibilidade e acelera a construção de testes.

## 📌 Dica: esta arquitetura foi desenhada para crescer. Com pequenos ajustes, é possível:

* Migrar de dicionários para banco de dados real (SQL ou NoSQL).
* Adicionar workers com Celery ou RQ.
* Introduzir autenticação OAuth2 e RBAC com baixo acoplamento.

---

⬅️ Voltar para o início