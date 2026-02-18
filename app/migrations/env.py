from __future__ import with_statement
from alembic import context
from logging.config import fileConfig
from flask import current_app

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = current_app.extensions['migrate'].db.metadata

def run_migrations_offline():
    context.configure(url=current_app.config.get("SQLALCHEMY_DATABASE_URI"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = current_app.extensions['migrate'].db.engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
