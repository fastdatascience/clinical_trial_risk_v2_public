import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

from app import models  # noqa # pylint: disable=unused-import
from app.config import DATABASE_URL as CONFIG_DATABASE_URL

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Database URL
DATABASE_URL: str | None = None
if CONFIG_DATABASE_URL:
    DATABASE_URL = CONFIG_DATABASE_URL
elif OS_ENV_DATABASE_URL := os.getenv("DATABASE_URL"):
    DATABASE_URL = OS_ENV_DATABASE_URL

if not DATABASE_URL:
    raise Exception("""
        Please configure the environment variables for PostgreSQL in the file .env to use Alembic.
        If Alembic is being used inside a GitHub action, configure the secret for the database URL on GitHub, check
        .secrets.example for an example.
    """)

# Set sqlalchemy.url
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = SQLModel.metadata


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
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    # capture tables and objects, excluding new model additions (nothing to
    # compare to)
    if type_ in ("table", "column") and compare_to is not None:
        # equate both versions to avoid triggering any comment ddl
        object.comment = compare_to.comment = "TEST"
    # but continue to include the object in the autogenerate comparison
    return False


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
