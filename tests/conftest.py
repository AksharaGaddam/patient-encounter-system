import os
import pytest
from alembic.config import Config
from alembic import command


@pytest.fixture(scope="session", autouse=True)
def maybe_run_alembic():
    """Run migrations when TEST_DATABASE_URL is provided (CI integration run).
    This runs once per test session and is a no-op locally unless TEST_DATABASE_URL is set.
    """
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        # Nothing to do for in-memory/local unit tests
        return

    # Run alembic upgrade head against TEST_DATABASE_URL
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", test_db_url)

    command.upgrade(cfg, "head")
