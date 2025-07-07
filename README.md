# 🚀 FastTrackAPI – Projeto Prisma

[![Coverage](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/FastTrackAPI---Projeto-Prisma)
---------- coverage: platform win32, python 3.12.6-final-0 -----------
Name                                                Stmts   Miss  Cover   Missing
TOTAL                                                1016    192    81%

Required test coverage of 80% reached. Total coverage: 82.36%
> **Cobertura de testes:** 82,36 % (mínimo exigido ≥ 80 %)

Este repositório é o resultado de uma mentoria prática em desenvolvimento **Backend** com **Python 3.12 + FastAPI**, cobrindo arquitetura limpa, segurança, testes, CI/CD e observabilidade.

---

## 📚 Sumário

| #     | Seção                                       | Arquivo                                  |
| ----- | ------------------------------------------- | ---------------------------------------- |
| 1     | [Introdução](docs/1_introducao.md)          | `docs/1_introducao.md`                   |
| 2     | [Visão Geral](docs/2_visao-geral.md)        | `docs/2_visao-geral.md`                  |
| 3     | [Objetivos](docs/3_objetivos.md)            | `docs/3_objetivos.md`                    |
| 4     | [Fundamentos de Arquitetura](docs/4_fundamentos-arquitetura.md) | `docs/4_fundamentos-arquitetura.md`      |
|   4.1 | [Arquitetura do Projeto](docs/4-1_arquitetura.md) | `docs/4-1_arquitetura.md`                |
|   4.2 | [Configuração por Ambiente + Fallback Seguro](docs/4-2_configuracao-ambiente.md) | `docs/4-2_configuracao-ambiente.md`      |
|   4.3 | [Dependências Reutilizáveis e Testáveis](docs/4-3_dependencias-reutilizaveis.md) | `docs/4-3_dependencias-reutilizaveis.md` |
| 5     | [Tecnologias & Boas Práticas](docs/5_tecnologias-boas-praticas.md) | `docs/5_tecnologias-boas-praticas.md`    |
|   5.1 | [Filtros e Paginação](docs/5-1_filtros-paginacao.md) | `docs/5-1_filtros-paginacao.md`          |
|   5.2 | [Cache com Redis](docs/5-2_cache-redis.md)  | `docs/5-2_cache-redis.md`                |
|   5.3 | [Observabilidade e Logs](docs/5-3_observabilidade-logs.md) | `docs/5-3_observabilidade-logs.md`       |
|   5.4 | [WebSockets e Arquivos](docs/5-4_websockets-arquivos.md) | `docs/5-4_websockets-arquivos.md`        |
|   5.5 | [Banco de Dados e Migrations](docs/5-5_banco-migrations.md) | `docs/5-5_banco-migrations.md`           |
|   5.6 | [Latência em Mocks](docs/5-6_latencia-mocks.md) | `docs/5-6_latencia-mocks.md`             |
| 6     | [Qualidade & Automação](docs/6_qualidade-automacao.md) | `docs/6_qualidade-automacao.md`          |
|   6.1 | [Testes Automatizados](docs/6-1_testes-automatizados.md) | `docs/6-1_testes-automatizados.md`       |
|   6.2 | [Pipeline de CI/CD](docs/6-2_pipeline-ci.md) | `docs/6-2_pipeline-ci.md`                |
| 7     | [Roadmap e Próximos Passos](docs/7_roadmap.md) | `docs/7_roadmap.md`                      |
| 8     | [Como Executar Localmente](docs/8_executar-localmente.md) | `docs/8_executar-localmente.md`          |
| 9     | [Referências](docs/9_referencias.md)         | `docs/9_referencias.md`                  |
| 10    | [Benchmark](docs/10_benchmark_documentacao.md) | `docs/10_benchmark_documentacao.md`      |

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

Adotamos **`Protocol`** + injecção de dependências para trocar facilmente implementações (mock ⇄ SQLAlchemy) sem tocar nos *endpoints*.

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

#### [Banco de Dados e Migrations](docs/5-5_banco-migrations.md)

TODO Descrição

#### [Latência em Mocks](docs/5-6_latencia-mocks.md)

Corrigimos um gargalo de 3 – 10 s por requisição: o `MockUserRepo` executava `bcrypt` a cada request. Agora o mock é **singleton** quando `ENVIRONMENT=test.inmemory`, reduzindo para ≈ 30 ms. Detalhes em `docs/5-6_latencia-mocks.md`.

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
