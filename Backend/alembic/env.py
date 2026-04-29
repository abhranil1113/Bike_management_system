from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# -------------------------
# Alembic Config
# -------------------------
config = context.config

# -------------------------
# Logging
# -------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------------
# SAFE FIX for % interpolation issue
# -------------------------
# Alembic configparser treats % as interpolation symbol
# So we escape it safely
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in .env")

safe_database_url = DATABASE_URL.replace("%", "%%")

config.set_main_option("sqlalchemy.url", safe_database_url)

# -------------------------
# Import models (IMPORTANT)
# -------------------------
from app.db.schema import Base  # keep your current structure

target_metadata = Base.metadata

# -------------------------
# Offline migrations
# -------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------
# Online migrations
# -------------------------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# -------------------------
# Run migrations
# -------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()