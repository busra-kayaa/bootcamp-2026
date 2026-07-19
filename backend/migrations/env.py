import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- BİZİM PROJENİN AYARLARI VE MODELLERİ ---
from app.core.config import get_settings
from app.core.database import Base
# Alembic'in tabloları (metadata) algılayabilmesi için modellerimizi mutlaka import etmeliyiz:
from app.models import Document, AnalysisJob 

# Alembic Config objesi (.ini dosyasından gelir)
config = context.config

# Loglama ayarları
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic'in değişiklikleri takip edeceği ana metadata
target_metadata = Base.metadata

# Projemizin .env ayarlarını çekiyoruz
settings = get_settings()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=settings.database_url, # URL'yi config.py'den alıyoruz
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Senkron migration koşturucu (async loop içinden çağrılır)."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode asenkron olarak."""
    
    # alembic.ini dosyasındaki url'yi ezip kendi ayarlarımızdakini koyuyoruz
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Asenkron event-loop'u başlatır."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()