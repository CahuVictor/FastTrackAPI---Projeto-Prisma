# 🚀 FastTrackAPI – Projeto Prisma

[![Coverage](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma)
---------- coverage: platform win32, python 3.12.6-final-0 -----------
Name                                                Stmts   Miss  Cover   Missing
TOTAL                                                1016    192    81%

Required test coverage of 80% reached. Total coverage: 82.36%

Este repositório faz parte de uma mentoria prática em desenvolvimento backend com Python e FastAPI, focado em boas práticas, segurança, testes automatizados e infraestrutura moderna.

---

## 📚 Sumário

* [Introdução](docs/1_introducao.md)
* [Visão Geral](docs/2_visao-geral.md)
* [Objetivos](docs/3_objetivos.md)
* [Fundamentos de Arquitetura](docs/4_fundamentos-arquitetura.md)

  * [Arquitetura do Projeto](docs/4-1_arquitetura.md)
  * [Configuração por Ambiente + Fallback Seguro](docs/4-2_configuracao-ambiente.md)
  * [Dependências Reutilizáveis e Testáveis](docs/4-3_dependencias-reutilizaveis.md)
* [Tecnologias & Boas Práticas](docs/5_tecnologias-boas-praticas.md)

  * [Filtros e Paginação](docs/5-1_filtros-paginacao.md)
  * [Cache com Redis](docs/5-2_cache-redis.md)
  * [Observabilidade e Logs](docs/5-3_observabilidade-logs.md)
  * [WebSockets e Arquivos](docs/5-4_websockets-arquivos.md)
  * [Banco de Dados e Migrations](docs/5-5_banco-migrations.md)
* [Qualidade & Automação](docs/6_qualidade-automacao.md)

  * [Testes Automatizados](docs/6-1_testes-automatizados.md)
  * [Pipeline de CI/CD](docs/6-2_pipeline-ci.md)
* [Roadmap e Próximos Passos](docs/7_roadmap.md)
* [Como Executar Localmente](docs/8_executar-localmente.md)
* [Benchmark](docs/10_benchmark_documentacao.md)
* [Referências](docs/9_referencias.md)

---

## 📖 Conteúdo das Seções

### [Introdução](docs/1_introducao.md)

* Eplicação sobre o Projeto Prisma

### [Visão Geral](docs/2_visao-geral.md)

* Visão Geral do Projeto

### [Objetivos](docs/3_objetivos.md)

* Descrição do Objetivo Geral e Objetivos Específicos

### [Fundamentos de Arquitetura](docs/4_fundamentos-arquitetura.md)

#### [Arquitetura do Projeto](docs/4-1_arquitetura.md)

* Estrutura geral das camadas (router, service, repository, schemas, models).
* Detalhes sobre bancos de dados interno e externo simulado.
* Fluxo de integração com APIs externas (OpenWeatherMap).

#### [Configuração por Ambiente + Fallback Seguro](docs/4-2_configuracao-ambiente.md)

* Explicação sobre os ambientes (`dev`, `test`, `prod`).
* Uso e gestão segura das variáveis de ambiente.

#### [Dependências Reutilizáveis e Testáveis](docs/4-3_dependencias-reutilizaveis.md)

* Explicação detalhada sobre protocolos e abstrações.
* Como criar mocks e substituir facilmente dependências para testes.

### [Tecnologias & Boas Práticas](docs/5_tecnologias-boas-praticas.md)

#### [Filtros e Paginação](docs/5-1_filtros-paginacao.md)

* Implementação da paginação in-memory com filtros dinâmicos.
* Exemplos e boas práticas adotadas para escalabilidade.

#### [Cache com Redis](docs/5-2_cache-redis.md)

* Explicação do uso do Redis para cache de requisições frequentes.
* Detalhes sobre estratégias (cache-aside), vantagens e implementação no código.

#### [Observabilidade e Logs](docs/5-3_observabilidade-logs.md)

* Estruturação e configuração de logs com `structlog`.
* Middleware implementado e exemplos práticos.

#### [WebSockets e Arquivos](docs/5-4_websockets-arquivos.md)

* Uso de WebSockets para comunicação em tempo real.
* Upload e download de arquivos CSV e JSON.

### [Qualidade & Automação](docs/6_qualidade-automacao.md)

#### [Testes Automatizados](docs/6-1_testes-automatizados.md)

* Explicação detalhada sobre estrutura dos testes unitários e integração.
* Justificativa das decisões técnicas tomadas durante o desenvolvimento dos testes.

#### [Pipeline de CI/CD](docs/6-2_pipeline-ci.md)

* Fluxo completo do GitHub Actions configurado.
* Ferramentas utilizadas (Ruff, MyPy, Bandit, Pytest, Codecov).

### [Roadmap e Próximos Passos](docs/7_roadmap.md)

* Evoluções planejadas para o projeto.
* Sugestões para melhorias futuras.

### [Como Executar Localmente](docs/8_executar-localmente.md)

* Guia passo a passo para configuração local.
* Instalação com Poetry e execução com Uvicorn.

### [Referências](docs/9_referencias.md)

* Links externos úteis e documentação adicional.

---

Cada seção contém um link para retornar ao índice principal:

```markdown
[⬅️ Voltar para o início](../README.md)
```
