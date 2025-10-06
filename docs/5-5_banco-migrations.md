# Banco de Dados e Migrations

## 1. Introdução

Este documento descreve a estrutura do banco de dados do projeto e a técnica de migrations utilizada com a ferramenta Alembic. É parte integrante da documentação técnica do sistema.

## 2. Estrutura do Banco de Dados

O banco de dados utilizado é PostgreSQL, com as seguintes entidades principais:

* **events**: representa eventos culturais com dados como título, descrição, data, cidade, participantes, views, e relacionamentos com local\_info e forecast\_info.
* **local\_infos**: representa informações do local onde o evento ocorre.
* **forecast\_infos**: representa previsões meteorológicas para o evento.

Esses modelos estão definidos nos seguintes arquivos:

* `app/models/models_event.py`
* `app/models/models_local_info.py`
* `app/models/models_forecast_info.py`

## 3. Migrations com Alembic

O Alembic é uma ferramenta do ecossistema SQLAlchemy capaz de Gerenciar evoluções/migrações no esquema do banco (criação, alteração ou exclusão de tabelas e campos) e Garantir que seu banco tenha sempre um esquema consistente com os modelos definidos na aplicação Python.

Alembic é a ferramenta escolhida para controlar versões do schema do banco. Permite:

* Criar automaticamente scripts de criação/atualização de tabelas via `alembic revision --autogenerate`
* Aplicar migrações com `alembic upgrade head`
* Garantir consistência entre os modelos Python e o banco

📌 Como o Alembic sabe qual banco usar?
O Alembic procura sua configuração de banco no arquivo chamado alembic.ini (que fica na raiz do seu projeto ou onde você executa o comando) no parâmetro `sqlalchemy.url`.

Configuração usada no `alembic.ini`:

```ini
script_location = migrations
sqlalchemy.url = postgresql://prisma:prisma123@localhost:5432/prisma_db
```

## 4. Processo de Criação e Atualização

1. Inicialização do Alembic:

   ```bash
   alembic init migrations
   ```

2. Criação dos modelos e importação em `migrations/env.py`

3. Criação de uma nova versão:

   ```bash
   alembic revision --autogenerate -m "create all tables"
   ```

4. Aplicação da migração:

   ```bash
   alembic upgrade head
   ```

Caso ocorra erro de versão faltante (ex: 'Can't locate revision e69fdb78a658'):

* Remover todos os arquivos da pasta `migrations/versions`
* Executar:

  ```sql
  DROP TABLE alembic_version;
  ```
* Gerar e aplicar nova versão

Caso ocorra outro erro e queira resetar a configuração do banco:

1. Apague o migration antigo (ou renomeie para backup)
2. Gere nova migração com os modelos agora corretamente importados
3. Aplique a nova migração

Executar:

  ```bash
  rm migrations/versions/*.py  # cuidado: isso remove TODAS as versões de migração
  alembic revision --autogenerate -m "create tables"
  alembic upgrade head
  ```


## 5. Por que é uma Solução Robusta

* **Reprodutibilidade**: permite qualquer dev recriar a estrutura do banco fiel aos modelos
* **Segurança**: controle de alterações de schema sem necessidade de alterar manualmente o banco
* **Histórico**: todas as mudanças ficam versionadas
* **Compatibilidade com CI/CD**: migrações podem ser aplicadas automaticamente em pipelines

## 6. Recomendações e Boas Práticas

* Sempre **versionar os arquivos `migrations/versions/*.py`** no Git
* Evitar usar o Alembic em ambiente de execução: aplique migrações apenas via comando ou CI
* Manter `alembic.ini` apontando para variável de ambiente se houver múltiplos bancos

---

**Próximo passo sugerido:** adicionar este documento como `docs/5-5_banco-migrations.md` no sumário, logo após `docs/5-4_websockets-arquivos.md`. Posso te ajudar a atualizar o sumário se quiser.

[⬅️ Voltar para o início](../README.md)
