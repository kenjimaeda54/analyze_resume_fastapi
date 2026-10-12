# analyzes-resume

API de análise e gestão de candidaturas a vagas. O candidato envia seu currículo (PDF/DOC/DOCX) para uma vaga, o arquivo é armazenado no Cloudflare R2 e uma notificação assíncrona é enviada ao n8n via fila Redis (RQ).

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI (Python 3.13) |
| Banco de dados | PostgreSQL + SQLAlchemy 2.0 |
| Migrations | Alembic |
| Fila / cache | Redis + RQ |
| Storage | Cloudflare R2 (compatível com S3 / boto3) |
| Notificação | Webhook n8n (via fila RQ) |
| Gerenciamento de deps | [uv](https://docs.astral.sh/uv/) |
| Validações | Pydantic, validate-docbr (CPF) |

---

## Arquitetura Hexagonal (Ports & Adapters)

O projeto segue a arquitetura hexagonal, também conhecida como *Ports and Adapters*. A ideia central é:

> **O núcleo de negócio (domain + application) nunca conhece infraestrutura.** Regras de negócio não importam se o dado vem do PostgreSQL, de um JSON, de um bucket R2 ou de uma fila Redis. Detalhes técnicos ficam nas bordas (adapters).

### As 4 camadas

```
app/
├── domain/            # Núcleo: regras de negócio puras (sem dependência de framework)
├── application/       # Casos de uso + contratos (ports) + DTOs
├── infrastructure/    # Implementações concretas (DB, R2, Redis) — "borda de entrada/saída"
└── adapters/          # Adaptadores HTTP (controllers, handlers) — "borda de entrada"
```

#### 1. `domain/` — O coração do sistema

Contém apenas regras de negócio, sem nenhuma importação de SQLAlchemy, FastAPI, boto3 ou qualquer infraestrutura.

| Subpasta | O que mora ali | Exemplo |
|---|---|---|
| `entities/` | Modelos de negócio (Pydantic BaseModel) | `Candidate`, `Vacancy`, `Application` |
| `enum/` | Enumerações de domínio | `CandidateStatus` (PENDING/APPROVED/REJECTED) |
| `exception/` | Exceções de negócio (`CandidateNotFound`, `VacancyNotFound`...) | Estendem `GeneralError` / `NotFoundError` de `base.py` |
| `validators/` | Validações puras de negócio | `validate_cpf.py` |

> **Regra de ouro:** se você importar algo de `infrastructure/` ou `adapters/` dentro de `domain/`, a arquitetura quebrou.

#### 2. `application/` — Orquestração e contratos

| Subpasta | O que mora ali | Exemplo |
|---|---|---|
| `ports/` | **Interfaces abstratas** (ABC) que o domínio precisa | `CandidateGatewayInterface`, `StorageR2GatewayInterface` |
| `use_cases/` | A lógica de orquestração: valida, consulta portas, toma decisão | `ApplyToVacancyUseCase` |
| `dto/request/` | Formas de entrada (o que a API recebe) | `CreateCandidate` |
| `dto/response/` | Formas de saída (o que a API retorna) | `ApplicationResponseDTO` |

As **ports** são o coração do desacoplamento. Por exemplo, o use case depende apenas da interface:

```python
# application/ports/storage_r2_gateway.py
class StorageR2GatewayInterface(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, file_path: str) -> str: ...

    @abstractmethod
    def delete_file(self, file_path: str) -> None: ...
```

O use case nunca sabe se o upload vai para R2, S3, LocalStack ou disco local — ele só chama `upload_file()`. A implementação concreta é injetada pelo controller (via FastAPI DI).

#### 3. `infrastructure/` — Implementações concretas

| Subpasta | O que mora ali | Exemplo |
|---|---|---|
| `database/models/` | Tabelas SQLAlchemy (`Base` do projeto) | `CandidateTable`, `VacancyTable` |
| `database/gateway/` | Implementações das ports de persistência | `CandidateGatewayImplementation` |
| `database/exceptions/` | Mappers de erro de IntegrityError → exceções de domínio | `map_candidate_integrity_error` |
| `storage/gateway/` | Implementação do storage (boto3/R2) | `StorageR2GatewayImplementation` |
| `storage/validators/` | Validação de magic bytes do currículo | `validate_resume_extension.py` |
| `notification/` | Fila RQ, config do Redis e tasks | `queue_config.py`, `notify_n8n_task.py` |

Cada gateway implementa uma port e traduz entre **entidade de domínio** (Pydantic) e **tabela** (SQLAlchemy) usando um mapper.

#### 4. `adapters/` — Borda HTTP

| Subpasta | O que mora ali | Exemplo |
|---|---|---|
| `controllers/` | Routers FastAPI: recebem request, montam gateways via DI, chamam use case | `candidate_controller.py` |
| `mapper/` | Conversores DTO ↔ Domínio ↔ Tabela | `CandidateMapper` |
| `handlers/` | Exception handlers globais (domínio → HTTP response) | `candidate_exception_handler.py` |
| `messages/` | Mensagens de erro por campo | `field_messages.py` |

### Fluxo de uma requisição (exemplo real: candidatura)

```
HTTP POST /candidate/{vacancy_id}/apply
        │
        ▼
┌─ adapters/controllers/candidate_controller.py ─────────────┐
│  1. Recebe Form + File                                       │
│  2. Valida DTO (CreateCandidate)                            │
│  3. Monta gateways: CandidateGatewayImplementation(db),     │
│     VacancyGatewayImplementation(db), StorageR2Gateway...   │
│  4. Injeta tudo no ApplyToVacancyUseCase e chama             │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ application/use_cases/candidate/apply_to_vacancy_use_case.py ─┐
│  1. validate_resume_extension()  (domain/validators ou infra)  │
│  2. validate_cpf()               (domain/validators)           │
│  3. candidate_gateway.get_candidate()   ← port → postgres      │
│  4. vacancy_gateway.get_by_vacancy_public_id() ← port → postgres│
│  5. storager2.upload_file()              ← port → R2           │
│  6. candidate_gateway.create/update()    ← port → postgres     │
│  7. application_gateway.create()         ← port → postgres     │
│  8. notification_gateway.notify()        ← port → Redis/RQ     │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
HTTP 201 { public_id, status }
```

### Regra de dependência (o diagrama que resume tudo)

```
        ┌──────────────────────────────────────────────┐
        │                  adapters                     │
        │  (controllers, mappers, handlers)             │
        └──────────────────────┬───────────────────────┘
                               │ depende de
                               ▼
        ┌──────────────────────────────────────────────┐
        │               application                    │
        │   (use_cases, ports, dtos)                   │
        └──────────────────────┬───────────────────────┘
                               │ depende de
                               ▼
        ┌──────────────────────────────────────────────┐
        │                 domain                        │
        │   (entities, enums, exceptions, validators)   │
        └──────────────────────────────────────────────┘

        infrastructure implementa as ports do application,
        mas o domain/application NUNCA importam infrastructure.
```

- `domain` não importa nada (é o centro)
- `application` importa apenas `domain`
- `infrastructure` implementa as ports de `application` e usa `domain`
- `adapters` importa `application` e `domain`, e liga tudo no FastAPI

---

## Pré-requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL rodando localmente
- Redis rodando localmente (necessário para a fila de notificações)
- Credenciais de um bucket Cloudflare R2
- (Opcional) Instância do n8n para receber os webhooks

## Configuração

### 1. Instalar dependências

```bash
uv sync
```

### 2. Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (o `.env` é ignorado pelo git):

```env
DB_NAME=analyzes_resume_db
DB_USER_NAME=postgres
DB_PASSWORD=sua_senha

R2_ACCESS_KEY_ID=sua_access_key
R2_SECRET_ACCESS_KEY=sua_secret_key
R2_BUCKET_NAME=resume
R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com

REDIS_URL=redis://localhost:9000

N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/candidatura-recebida
```

### 3. Banco de dados — conexão passo a passo

A conexão com o PostgreSQL foi configurada manualmente (sem lib extra de settings) em `app/infrastructure/database/database.py`. O fluxo é:

#### Passo 3.1 — Carregar as variáveis de ambiente

```python
# app/infrastructure/database/database.py
import os
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env da raiz do projeto

database_password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")
database_user_name = os.getenv("DB_USER_NAME")
```

#### Passo 3.2 — Montar a URL de conexão e criar o Engine

```python
DATABASE_URL = f"postgresql://{database_user_name}:{database_password}@localhost/{database_name}"

engine = create_engine(DATABASE_URL)
```

> O SQLAlchemy usa essa URL para se conectar ao PostgreSQL via driver `psycopg2` (instalado como `psycopg2-binary` no `pyproject.toml`).

#### Passo 3.3 — Criar a SessionFactory e a Base dos models

```python
SessionLocal = sessionmaker(
    autocommit=False,
    class_=Session,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass
```

- `SessionLocal` — factory que abre uma sessão (uma conexão/transação) por requisição
- `Base` — classe pai de **todas** as tabelas SQLAlchemy (`CandidateTable`, `VacancyTable`, `ApplicationTable` herdam dela)

#### Passo 3.4 — Dependency Injection no FastAPI

```python
def get_database():
    db = SessionLocal()
    try:
        yield db          # abre a sessão e disponibiliza para o endpoint
    finally:
        db.close()        # fecha a sessão sempre, mesmo com erro

depends_db = Annotated[Session, Depends(get_database)]
```

`depends_db` é o "apelido" usado nos controllers. Quando um endpoint declara `db: depends_db`, o FastAPI chama `get_database()`, abre uma sessão, injeta no endpoint e fecha ao final:

```python
# exemplo de uso no controller
def apply_candidate_use_case_gateway(db: depends_db, ...):
    candidate_gateway = CandidateGatewayImplementation(db)  # recebe a Session
    ...
```

> A mesma lógica se repete para as outras infraestruturas: `depends_storage` (R2) e `depends_notification_gateway` (Redis/RQ) seguem o padrão factory + `Annotated[..., Depends(...)]`.

#### Passo 3.5 — Criar o banco (uma única vez)

Crie o banco de dados no PostgreSQL:

```sql
CREATE DATABASE analyzes_resume_db;
```

#### Passo 3.6 — Alembic: inicialização (feito com `alembic init`)

O Alembic foi configurado com o comando de inicialização:

```bash
uv run alembic init alembic
```

Esse comando cria:

```
alembic/
├── env.py              # script executado a cada migration (configura conexão e metadata)
├── script.py.mako      # template para novas migrations
└── versions/           # pasta onde ficam as migrations geradas
alembic.ini             # arquivo de configuração do Alembic
```

#### Passo 3.7 — Configurar o `alembic.ini`

Ajuste o caminho das migrations no `alembic.ini`:

```ini
[alembic]
script_location = %(here)s/alembic
sqlalchemy.url =
```

> A `sqlalchemy.url` fica **vazia** no ini — ela é setada em tempo de execução pelo `env.py`, lendo o `.env`.

#### Passo 3.8 — Configurar o `alembic/env.py`

O `env.py` é o coração da integração. Ele precisa:

**1) Importar a Base do projeto e todas as tabelas** (mesmo sem usar diretamente — o autogenerate precisa delas registradas no metadata):

```python
# alembic/env.py
from app.infrastructure.database.database import Base
from app.infrastructure.database.models.candidate_table import CandidateTable
from app.infrastructure.database.models.vacancy_table import VacancyTable
from app.infrastructure.database.models.application_table import ApplicationTable
```

**2) Montar a URL lendo o `.env` e setar no config:**

```python
load_dotenv()

database_password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")
database_user_name = os.getenv("DB_USER_NAME")

database_url = f"postgresql+psycopg2://{database_user_name}:{database_password}@localhost/{database_name}"
config.set_main_option("sqlalchemy.url", database_url)
```

**3) Apontar o metadata do Alembic para o metadata do projeto:**

```python
target_metadata = Base.metadata
```

> Com isso, o Alembic consegue comparar o estado das tabelas no código versus o estado no banco e gerar o diff automaticamente.

#### Passo 3.9 — Gerar e aplicar migrations

A partir daqui, o fluxo de trabalho com migrations é:

```bash
# 1. Após criar/alterar um model em infrastructure/database/models/, gere a migration:
uv run alembic revision --autogenerate -m "create_candidate_table"

# 2. Aplique no banco:
uv run alembic upgrade head
```

O autogenerate compara `Base.metadata` (código) com o schema real (banco) e gera o arquivo em `alembic/versions/`.

Comandos úteis para inspecionar o estado:

```bash
uv run alembic current   # qual migration o banco está
uv run alembic heads     # qual a última migration do código
uv run alembic history   # histórico completo
```

> **Lembrete:** sempre rode os comandos do Alembic com `uv run` para que rode dentro do ambiente virtual do projeto.

### 4. Redis — conexão passo a passo

O projeto usa o Redis como broker da fila `notifications` (RQ). A porta utilizada é a **9000** (definida no `.env`, no `Start Redis` e no `Worker`).

#### Como o Redis se conecta no código

A configuração está em `app/infrastructure/notification/queue_config.py`:

```python
# app/infrastructure/notification/queue_config.py
load_dotenv()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

redis_connection = Redis.from_url(redis_url)
notification_queue = Queue("notifications", connection=redis_connection)

def get_notification_gateway() -> RQNotificationGatewayImplementation:
    return RQNotificationGatewayImplementation(queue=notification_queue)

depends_notification_gateway = Annotated[RQNotificationGatewayImplementation, Depends(get_notification_gateway)]
```

Fluxo:

1. Lê a `REDIS_URL` do `.env` (neste projeto: `redis://localhost:9000`)
2. Cria uma conexão `Redis.from_url(...)`
3. Cria a fila `Queue("notifications", connection=...)`
4. Expõe via DI (`depends_notification_gateway`) para os controllers injetarem no use case
5. O use case chama `notification_gateway.notify_new_application(...)` que enfileira a task no RQ

#### Subindo o Redis

```bash
# macOS (Homebrew)
brew services start redis

# Linux / manual (porta 9000, igual ao projeto)
redis-server --port 9000

# Docker
docker run -d --name redis -p 9000:9000 redis:latest --port 9000
```

> No PyCharm isso é automático: a configuração `Start Redis` executa `redis-server --port 9000 --daemonize yes` via *Before Launch* (ver seção [Rodando no PyCharm](#rodando-no-pycharm-completo)).

#### Visualizando localmente com o RedisInsight

O [RedisInsight](https://redis.io/insight/) é a ferramenta oficial da Redis para inspecionar bancos Redis localmente (ver chaves, filas, consumo de memória, etc.).

Para conectar no projeto:

1. Abra o **RedisInsight**
2. Clique em **Connect to Redis database** (ou **Connect using database** / **Add Redis Database**)
3. Selecione a opção de conectar em um banco **existente** (*Connect an existing Redis database*)
4. Preencha os campos:
   - **Host:** `localhost`
   - **Port:** `9000`  ← troque da porta padrão `6379` para `9000`, que é a porta que este projeto usa
   - **Name:** `analyzes-resume` (ou o nome que preferir)
5. Clique em **Test Connection** para testar a conexão
6. Se der sucesso, clique em **Add Redis Database** (ou **Save**)

> **Verificação:** depois de adicionado, abra o banco no RedisInsight e vá na seção **Queues** (ou **Redis Lists**) — a fila `notifications` aparecerá assim que o Worker estiver rodando e alguma candidatura for processada.

### 5. Worker de notificações

O worker do RQ processa as tasks enfileiradas na fila `notifications` (webhook n8n). No PyCharm ele já roda junto via configuração `Worker` / `Full Project`. Manualmente:

```bash
uv run rq worker notifications --url redis://localhost:9000 --worker-class rq.SimpleWorker --with-scheduler
```

O que cada flag faz:

| Flag | Descrição |
|---|---|
| `notifications` | Nome da fila que o worker vai consumir (mesma do `queue_config.py`) |
| `--url redis://localhost:9000` | Endereço do Redis (porta 9000 deste projeto) |
| `--worker-class rq.SimpleWorker` | Worker síncrono simples (adequado para dev local) |
| `--with-scheduler` | Habilita o scheduler do RQ (necessário para os retries com `Retry(interval=...)`) |

## Como rodar a aplicação

O projeto tem **3 processos** que precisam rodar juntos:

| Processo | O que faz | Configuração PyCharm |
|---|---|---|
| Redis | Broker da fila (porta 9000) | `Start Redis` (Before Launch) |
| API FastAPI | Sobe o servidor em `:8000` | `main` |
| Worker RQ | Consome a fila e chama o n8n | `Worker` |

### Opção 1 — PyCharm (recomendado)

Use a configuração **Full Project** (ver detalhes na seção [Rodando no PyCharm](#rodando-no-pycharm-completo)).

### Opção 2 — Terminal (3 terminais separados)

```bash
# Terminal 1 — Redis (porta 9000)
redis-server --port 9000

# Terminal 2 — API
uv run uvicorn app.main:app --reload

# Terminal 3 — Worker
uv run rq worker notifications --url redis://localhost:9000 --worker-class rq.SimpleWorker --with-scheduler
```

A API sobe em `http://localhost:8000`. Verificação de saúde:

```bash
curl http://localhost:8000/healthy
```

Documentação interativa (Swagger): `http://localhost:8000/docs`

---

## Rodando no PyCharm (completo)

O projeto possui run configurations versionadas. Existem **4 configurações**:

| Configuração | Arquivo | Tipo | Descrição |
|---|---|---|---|
| **Full Project** | `run/Full Project.run.xml` | **Compound** | ⭐ **Forma principal de rodar.** Executa `Worker` + `main` em paralelo |
| `main` | `run/main.run.xml` | Python | Sobe a API FastAPI (`app/main.py`) — tem *Before Launch* que inicia o Redis |
| `Worker` | `run/Worker.run.xml` | Python | Roda o worker RQ (`rq.cli worker notifications`) consumindo a fila |
| `Start Redis` | `run/Start Redis.run.xml` | Shell Script | Executa `redis-server --port 9000 --daemonize yes` |

### Full Project — a configuração principal

O **Full Project** é uma *Compound Run Configuration*: ele dispara várias configurações **em paralelo** com um único clique em **Run**:

- `Worker` — worker RQ consumindo a fila `notifications` (Redis porta 9000)
- `main` — API FastAPI (que por sua vez dispara o `Start Redis` via *Before Launch*)

Para usar:

1. No canto superior direito do PyCharm, selecione **Full Project** no seletor de run configurations
2. Clique em **Run** (▶)
3. Verifique que três abas/terminais abriram:
   - **Start Redis** — Redis subindo na porta 9000 (daemonizado, encerra a aba rapidamente)
   - **main** — API FastAPI rodando em `http://localhost:8000`
   - **Worker** — worker RQ conectado na fila `notifications`

> **Verificação:** a aba `main` deve mostrar algo como `Uvicorn running on http://0.0.0.0:8000`, e a aba `Worker` deve mostrar `RQ worker started, version 2.x` sem erros de conexão com o Redis.

### Como o `main` inicia o Redis automaticamente (Before Launch)

A configuração `main` já está preparada para **iniciar o Redis automaticamente antes da aplicação** via a seção *Before Launch* (configurada no `run/main.run.xml`):

```xml
<method v="2">
  <option name="RunConfigurationTask" enabled="true"
          run_configuration_name="Start Redis"
          run_configuration_type="ShConfigurationType" />
</method>
```

Caso precise reconfigurar manualmente no PyCharm:

1. Abra **Run > Edit Configurations...**
2. Selecione a configuração **main**
3. Clique no texto em azul **Modify options** (localizado logo acima do campo *Python Interpreter*)
4. No menu suspenso, procure por **Before launch** e selecione essa opção
5. A seção *Before launch* aparecerá na parte inferior da janela. Clique no botão **+**, selecione **Run Another Configuration** (ou **Run External Tool**) e adicione a configuração **Start Redis**

### Ajuste da Run Configuration `Start Redis`

O interpretador no ficheiro `run/Start Redis.run.xml` está definido por padrão para `/bin/zsh`. É possível que precise de ajustá-lo caso o seu sistema não utilize esse caminho ou esteja no Windows.

O script executado é:

```bash
redis-server --port 9000 --daemonize yes
```

| Flag | Descrição |
|---|---|
| `--port 9000` | Sobe o Redis na porta 9000 (igual ao `.env` e ao `Worker`) |
| `--daemonize yes` | Sobe em background e libera o terminal imediatamente |

Como ajustar o interpretador no PyCharm:

1. Vá ao menu superior e clique em **Run > Edit Configurations...**
2. No painel esquerdo, expanda **Shell Script** e selecione **Start Redis**
3. No campo **Interpreter path**, altere de acordo com o seu sistema:
   - **macOS / Linux:** Defina como `/bin/sh`, `/bin/bash` ou o caminho retornado por `which zsh` / `which bash` no seu terminal
   - **Windows (Cmd / PowerShell):** Defina como `cmd.exe` ou `powershell.exe`
   - **Windows (WSL):** Defina como `wsl.exe`
4. Clique em **Apply** e **OK**

> **Verificação:** ao clicar em **Run** na configuração `main` (ou `Full Project`), a aba `Start Redis` deverá abrir sem erros de interpretador e, como usa `--daemonize yes`, o Redis fica rodando em background.

### Como o `Worker` está configurado

A configuração `Worker` roda o worker do RQ como módulo Python (`rq.cli`) com os parâmetros:

```
worker notifications --url redis://localhost:9000 --worker-class rq.SimpleWorker --with-scheduler
```

- Usa o interpretador do projeto (`uv (analyzes_resume)`)
- Carrega o `.env` automaticamente (`ENV_FILES = $PROJECT_DIR$/.env`)
- Conecta direto na porta 9000 (não depende do `.env` para o `--url`, está hardcoded nos parâmetros)

### Resumo do fluxo ao clicar em Run (Full Project)

```
Full Project (Compound)
├── Before Launch (via main) ──► Start Redis
│                                  redis-server --port 9000 --daemonize yes
│
├── main ──────────────────────► API FastAPI em http://localhost:8000
│                                  (conecta PostgreSQL + Redis:9000 + R2)
│
└── Worker ────────────────────► rq worker notifications
                                   (consome fila do Redis:9000, chama n8n)
```

---

## Endpoints

### `GET /healthy`

Verificação de saúde da aplicação.

**Resposta (200):**

```json
{ "status": "200" }
```

### `POST /candidate/{vacancy_id}/apply`

Envia a candidatura de um candidato a uma vaga, com upload do currículo.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `cpf` | string | ✅ | CPF do candidato (validado) |
| `name` | string | ✅ | Nome do candidato |
| `email` | string | ✅ | E-mail do candidato |
| `resume` | file | ✅ | Currículo (PDF, DOC ou DOCX) |
| `vacancy_id` | path param | ✅ | Public ID da vaga |

**Resposta de sucesso (201):**

```json
{
  "public_id": "uuid-da-candidatura",
  "status": "pending"
}
```

**Erros possíveis:**

| Status | Exceção | Descrição |
|---|---|---|
| 422 | `ValidationError` / `CandidateCpfException` | Dados inválidos ou CPF inválido |
| 404 | `VacancyNotFound` | Vaga não encontrada |
| 409 | `ApplicationAlreadyExistsException` | Candidatura já existente para a vaga |
| 409 | `CandidateConflictException` | Conflito de CPF/e-mail com outro candidato |
| 415/400 | `ResumeInvalidExtensionException` | Extensão de currículo inválida |

### Fluxo da candidatura

1. Valida a extensão/magic bytes do currículo (PDF/DOC/DOCX)
2. Valida o CPF
3. Consulta candidato e vaga no banco
4. Faz upload do currículo no Cloudflare R2
5. Cria ou atualiza o candidato e registra a candidatura
6. Enfileira notificação assíncrona (RQ) para o webhook do n8n — com retry (3 tentativas: 10s, 30s, 60s)
7. Retorna o `public_id` e o `status` da candidatura

---

## Como adicionar uma nova feature (guia passo a passo)

Vamos usar um exemplo real e prático: **criar um endpoint de listagem de vagas** (`GET /vacancy`). O mesmo passo a passo serve para qualquer novo recurso.

### Passo 1 — Entidade de domínio

Crie (ou reutilize) a entidade em `app/domain/entities/`:

```python
# app/domain/entities/vacancy.py
from pydantic import BaseModel

class Vacancy(BaseModel):
    public_id: str | None = None
    id: int | None = None
    title: str
    description: str
    company: str
```

> A entidade é um Pydantic puro — sem SQLAlchemy, sem FastAPI.

### Passo 2 — Port (interface) em `application/ports/`

Defina o contrato que o domínio espera, sem importar infraestrutura:

```python
# app/application/ports/vacancy_gateway.py
from abc import ABC, abstractmethod
from app.domain.entities.vacancy import Vacancy

class VacancyGatewayInterface(ABC):

    @abstractmethod
    def create_vacancy(self, vacancy: Vacancy): ...

    @abstractmethod
    def get_vacancy(self, vacancy_id: int) -> Vacancy | None: ...

    @abstractmethod
    def get_by_vacancy_public_id(self, public_id: str) -> Vacancy | None: ...
```

> **Sempre crie a port antes da implementação.** O use case vai depender só dessa interface.

### Passo 3 — Tabela SQLAlchemy em `infrastructure/database/models/`

```python
# app/infrastructure/database/models/vacancy_table.py
import uuid
from sqlalchemy import Integer, String, DateTime, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.database import Base

class VacancyTable(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, server_default=text("gen_random_uuid()"), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    delete_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
```

**Importante:** a tabela deve ser importada em `alembic/env.py` para o autogenerate funcionar:

```python
# alembic/env.py
from app.infrastructure.database.models.vacancy_table import VacancyTable  # ← adicione aqui
```

### Passo 4 — Mapper (Tabela ↔ Domínio)

Crie em `app/adapters/mapper/`:

```python
# app/adapters/mapper/vacancy_mapper.py
from app.domain.entities.vacancy import Vacancy
from app.infrastructure.database.models.vacancy_table import VacancyTable

class VacancyMapper:
    @staticmethod
    def to_domain_from_table(table: VacancyTable) -> Vacancy:
        return Vacancy(
            id=table.id,
            public_id=str(table.public_id),
            title=table.title,
            description=table.description,
            company=table.company,
        )
```

### Passo 5 — Gateway Implementation em `infrastructure/database/gateway/`

Implemente a port, traduzindo domínio ↔ tabela. Trate erros de integridade e faça rollback:

```python
# app/infrastructure/database/gateway/vacancy_gateway_implementation.py
from sqlalchemy.orm import Session
from app.adapters.mapper.vacancy_mapper import VacancyMapper
from app.application.ports.vacancy_gateway import VacancyGatewayInterface
from app.domain.entities.vacancy import Vacancy
from app.infrastructure.database.models.vacancy_table import VacancyTable

class VacancyGatewayImplementation(VacancyGatewayInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_by_vacancy_public_id(self, public_id: str) -> Vacancy | None:
        statement = select(VacancyTable).where(VacancyTable.public_id == public_id)
        table = self.db.execute(statement).scalar_one_or_none()
        return VacancyMapper.to_domain_from_table(table) if table else None
```

> **Padrão do projeto:** o gateway recebe um `Session` no construtor, e o controller é quem cria o gateway e injeta no use case.

### Passo 6 — Use Case em `application/use_cases/`

O use case orquestra a lógica usando **apenas as ports**:

```python
# app/application/use_cases/vacancy/list_vacancies_use_case.py
from app.application.ports.vacancy_gateway import VacancyGatewayInterface
from app.domain.entities.vacancy import Vacancy

class ListVacanciesUseCase:
    def __init__(self, vacancy_gateway: VacancyGatewayInterface):
        self.vacancy_gateway = vacancy_gateway

    def execute(self) -> list[Vacancy]:
        return self.vacancy_gateway.list_vacancies()
```

### Passo 7 — DTOs (request/response) em `application/dto/`

```python
# app/application/dto/response/vacancy_response_dto.py
from pydantic import BaseModel, Field

class VacancyResponseDTO(BaseModel):
    public_id: str
    title: str
    company: str
```

### Passo 8 — Exceção de domínio (se necessário)

```python
# app/domain/exception/vacancy/vacancy_not_found.py
from app.domain.exception.base import NotFoundError

class VacancyNotFound(NotFoundError):
    def __init__(self, vacancy_id: str):
        super().__init__(
            error_code="VACANCY_NOT_FOUND",
            message=f"Vacancy {vacancy_id} not found.",
        )
```

E o exception handler em `app/adapters/handlers/vacancy/`:

```python
# app/adapters/handlers/vacancy/vacancy_exception_handler.py
from fastapi.responses import JSONResponse
from app.domain.exception.base import ErrorResponse
from app.domain.exception.vacancy.vacancy_not_found import VacancyNotFound

async def vacancy_not_found_exception(request, exception: VacancyNotFound):
    error = ErrorResponse(
        http_status_code=404,
        error_code=exception.error_code,
        message=str(exception),
    )
    return JSONResponse(status_code=404, content=error.model_dump(exclude_none=True))
```

Registre o handler no `app/main.py`:

```python
app.add_exception_handler(VacancyNotFound, vacancy_not_found_exception)
```

### Passo 9 — Controller em `adapters/controllers/`

O controller é o **único lugar** que conhece infraestrutura. Ele monta os gateways e injeta no use case:

```python
# app/adapters/controllers/vacancy_controller.py
from fastapi import APIRouter, Depends
from typing import Annotated
from app.application.use_cases.vacancy.list_vacancies_use_case import ListVacanciesUseCase
from app.infrastructure.database.database import depends_db
from app.infrastructure.database.gateway.vacancy_gateway_implementation import VacancyGatewayImplementation

router = APIRouter(prefix="/vacancy", tags=["Vacancy"])

def list_vacancies_use_case(db: depends_db) -> ListVacanciesUseCase:
    vacancy_gateway = VacancyGatewayImplementation(db)
    return ListVacanciesUseCase(vacancy_gateway=vacancy_gateway)

@router.get("/")
async def list_vacancies(
    use_case: Annotated[ListVacanciesUseCase, Depends(list_vacancies_use_case)]
):
    return use_case.execute()
```

### Passo 10 — Registrar o router no `main.py`

```python
# app/main.py
from app.adapters.controllers import candidate_controller, vacancy_controller

app.include_router(vacancy_controller.router)
```

### Passo 11 — Migration

```bash
uv run alembic revision --autogenerate -m "create_vacancy_table"
uv run alembic upgrade head
```

### Checklist rápido

```
□ domain/entities/          → entidade Pydantic
□ domain/exception/         → exceção de negócio (se necessário)
□ application/ports/        → interface abstrata (ABC)
□ application/use_cases/    → orquestração usando apenas as ports
□ application/dto/          → DTOs de request/response
□ infrastructure/database/models/ → tabela SQLAlchemy + import em alembic/env.py
□ infrastructure/database/gateway/ → implementação da port com Session
□ adapters/mapper/          → conversor tabela ↔ domínio
□ adapters/controllers/     → router + factory do use case via DI
□ adapters/handlers/        → exception handler (se houver exceção nova)
□ main.py                   → app.include_router(...) + add_exception_handler(...)
□ alembic                   → revision --autogenerate + upgrade head
```

---

## Como trocar/implementar uma infraestrutura (ex: storage)

Esse é o poder da arquitetura hexagonal. Suponha que você queira trocar o Cloudflare R2 por S3 da AWS, MinIO ou armazenamento local:

### O que NÃO muda

- `domain/` — nada
- `application/use_cases/` — nada (ele só conhece a port `StorageR2GatewayInterface`)
- `application/ports/` — nada (a interface continua igual)

### O que você cria/troca

1. **Crie uma nova implementação** em `app/infrastructure/storage/gateway/`:

```python
# storage_s3_gateway_implementation.py (novo)
class StorageS3GatewayImplementation(StorageR2GatewayInterface):
    def __init__(self, bucket_name: str, ...):
        self.client = boto3.client("s3", ...)

    def upload_file(self, file_content: bytes, file_path: str) -> str:
        # implementação S3
        ...

    def delete_file(self, file_path: str) -> None:
        # implementação S3
        ...
```

2. **Troque a factory** em `app/infrastructure/storage/storage.py` (o único ponto que o controller conhece):

```python
def get_storage() -> StorageR2GatewayInterface:  # ← retorna a interface, não a classe
    return StorageS3GatewayImplementation(...)   # ← era StorageR2GatewayImplementation
```

3. **Adicione as variáveis de ambiente** novas no `.env` e no `storage.py`

Pronto. O controller, o use case e o domínio continuam funcionando sem nenhuma alteração. Essa é a dependência invertida em ação: **o detalhe (S3/R2) depende da abstração (port), nunca o contrário**.

> Para qualquer outra infraestrutura (banco de dados, fila, cache), o padrão é o mesmo: nova implementação da port + troca na factory/DI.

---

## Estrutura de pastas

```
.
├── alembic/                          # Migrations
│   └── versions/
├── app/
│   ├── adapters/                     # Borda HTTP
│   │   ├── controllers/              # Routers FastAPI
│   │   ├── handlers/                 # Exception handlers globais
│   │   ├── mapper/                   # Conversores DTO ↔ Domínio ↔ Tabela
│   │   └── messages/                 # Mensagens de erro por campo
│   ├── application/                  # Casos de uso e contratos
│   │   ├── dto/
│   │   │   ├── request/
│   │   │   └── response/
│   │   ├── ports/                    # Interfaces abstratas (ABC)
│   │   └── use_cases/
│   ├── domain/                       # Núcleo de negócio (puro)
│   │   ├── entities/
│   │   ├── enum/
│   │   ├── exception/
│   │   └── validators/
│   ├── infrastructure/               # Implementações concretas
│   │   ├── database/
│   │   │   ├── exceptions/           # IntegrityError → exceção de domínio
│   │   │   ├── gateway/              # Implementação das ports de persistência
│   │   │   ├── models/               # Tabelas SQLAlchemy
│   │   │   └── database.py           # Engine, Session, Base
│   │   ├── notification/             # Redis + RQ + tasks
│   │   └── storage/                  # Cloudflare R2 (boto3)
│   └── main.py                       # Entry point FastAPI
├── run/                              # Run configurations do PyCharm (todas juntas)
│   ├── Full Project.run.xml          # Compound: Worker + main em paralelo
│   ├── main.run.xml                  # API FastAPI (Before Launch: Start Redis)
│   ├── Worker.run.xml                # Worker RQ (fila notifications, Redis:9000)
│   └── Start Redis.run.xml           # redis-server --port 9000 --daemonize yes
├── alembic.ini
├── pyproject.toml
└── .env                              # Não versionado
```

## Notas

- O arquivo `.env` **não é versionado** (ver `.gitignore`). Nunca commite credenciais.
- O Redis deste projeto roda na **porta 9000** (não na 6379 padrão) — `.env`, `Start Redis` e `Worker` estão alinhados nessa porta.
- O upload do currículo valida o conteúdo por magic bytes, não apenas pela extensão do arquivo.
- Em caso de falha após o upload do currículo, o arquivo é automaticamente removido do storage (rollback).
- As run configurations são versionadas na pasta `run/` (`*.run.xml`). Após clonar o projeto, ajuste apenas o interpretador da configuração `Start Redis` (ver seção PyCharm).
- **Para rodar o projeto completo, use sempre a configuração `Full Project`** no PyCharm — ela sobe Worker + API juntos (e o Redis via Before Launch).
- **Nunca** importe `infrastructure/` ou `adapters/` dentro de `domain/` ou `application/use_cases/`. Se precisar de algo novo, crie uma port.
