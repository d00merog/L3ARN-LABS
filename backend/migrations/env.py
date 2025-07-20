from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config.settings import settings
from core.database import Base

# Import models so that metadata is populated
from api.courses import models as course_models  # noqa: F401
from api.users import models as user_models  # noqa: F401
from api.auth import models as auth_models  # noqa: F401
from api.notifications import models as notification_models  # noqa: F401
from api.gamification import models as gamification_models  # noqa: F401
from api.achievements import models as achievement_models  # noqa: F401
from api.lessons import models as lesson_models  # noqa: F401
from api.recommendations import routes as recommendation_models  # noqa: F401
from api.gradebook import models as gradebook_models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

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

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
