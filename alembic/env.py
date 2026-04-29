import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# app/ modulini Python path ga qo'shish (Render uchun muhim)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Modellarni import qilish (autogenerate uchun kerak)
from app.database import Base
from app.models import user, poll, option, vote  # noqa: F401

target_metadata = Base.metadata


def get_url() -> str:
    """
    DATABASE_URL ni environment variable dan o'qiydi.
    Neon.tech va boshqa providerlar 'postgres://' yuboradi,
    SQLAlchemy 2.x esa 'postgresql://' talab qiladi — shuning uchun replace.
    """
    url = os.getenv("DATABASE_URL", "")
    if not url:
        # Lokal ishlab chiqish uchun .env fayldan o'qish
        try:
            from app.config import settings
            url = settings.DATABASE_URL
        except Exception:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set!"
            )
    # Neon / Heroku / Render → postgres:// → postgresql://
    return url.replace("postgres://", "postgresql://", 1)


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
