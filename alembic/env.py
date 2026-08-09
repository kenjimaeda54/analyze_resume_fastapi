import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import pool
from app.infrastructure.database.database import Base
from app.infrastructure.database.models.candidate_table import CandidateTable
from app.infrastructure.database.models.vacancy_table import VacancyTable
from app.infrastructure.database.models.application_table import  ApplicationTable

from alembic import context


#para comparar ou pegar mensagens de erro do alembic nas migrações roda os seguintes comndaos
#alembic current
#alembic heads
#lembrnado que precisa eta no ambiente virtual uv run por exemplo no meu caso que uso o uv
#da para identificar se uma migration falhou sej


#lembran que precisa importar as tabelas aqui mesmo sem usar
##primerio precisa rodar alembic init alembi
##depois alterar o Base metadata para o Base do projeto
##depois criar tabela alembic revision --autogenerate -m "nome da tabela"
##depois alembic upgrade head
##em times semrpe alembic upgrade head
##lembranod uqe precisa estar no modo virtual se estiver usando uv(uv run nome do comando)

load_dotenv()

config = context.config

database_password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")
database_user_name = os.getenv("DB_USER_NAME")

#configurar o database
database_url = f"postgresql+psycopg2://{database_user_name}:{database_password}@localhost/{database_name}"
config.set_main_option("sqlalchemy.url", database_url)


fileConfig(config.config_file_name)


##alterar o Base do projeto
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
