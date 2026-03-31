from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. Import your existing connection and Base
from app.db.session import DATABASE_URL, engine, Base
# Ensure all models are imported so Alembic "sees" the tables
from app.models.business import Business, Category 

# 2. SET THE METADATA CORRECTLY
target_metadata = Base.metadata

# 3. Handle the Alembic Config
config = context.config

# ESCAPE the percent signs for the internal ConfigParser
if DATABASE_URL:
    escaped_url = DATABASE_URL.replace('%', '%%')
    config.set_main_option("sqlalchemy.url", escaped_url)

# 4. Setup Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. Object filter to ignore PostGIS/System tables
def include_object(object, name, type_, reflected, compare_to):
    ignored_tables = [
        "spatial_ref_sys", 
        "geography_columns", 
        "geometry_columns", 
        "raster_columns", 
        "raster_overviews"
    ]
    if type_ == "table" and name in ignored_tables:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object  # Added here
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Using the verified engine from session.py
    connectable = engine 

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object  # Added here
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()