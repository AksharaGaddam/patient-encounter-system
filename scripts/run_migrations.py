"""Run Alembic migrations programmatically.

Usage:
  python -m scripts.run_migrations

This reads DATABASE_URL or TEST_DATABASE_URL from the environment.
"""
from alembic.config import Config
from alembic import command
import os

cfg = Config("alembic.ini")
# allow an env override
db = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL")
if db:
    cfg.set_main_option("sqlalchemy.url", db)

if __name__ == "__main__":
    print("Running alembic upgrade head against:", cfg.get_main_option("sqlalchemy.url"))
    command.upgrade(cfg, "head")
    print("Migrations applied.")
