"""Validate required DB secrets and formats.

Usage:
  python -m scripts.validate_secrets

This is intended to be run in CI (with secrets provided as env vars) or locally to check .env values.
Exits with code 0 on success, non-zero on failure.
"""
import os
import sys
from urllib.parse import urlparse

PLACEHOLDERS = {"changeme", "your_db_user", "your_db_password", "your_db_name", "127.0.0.1"}


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    v = value.strip()
    if v == "":
        return True
    if v in PLACEHOLDERS:
        return True
    return False


def validate_database_url(name: str, url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        print(f"ERROR: {name} is not a valid URL: {url}")
        return False

    if parsed.scheme not in ("mysql", "mysql+pymysql", "postgres", "postgresql"):
        print(f"WARNING: {name} has unusual scheme '{parsed.scheme}'. Expected 'mysql' or 'postgres'.")

    if not parsed.hostname or not parsed.username or not parsed.path:
        print(f"ERROR: {name} must include hostname, username and database name: {url}")
        return False

    if is_placeholder(parsed.username) or is_placeholder(parsed.hostname) or parsed.path in ("", "/"):
        print(f"ERROR: {name} contains placeholder values: {url}")
        return False

    return True


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    test_db_url = os.getenv("TEST_DATABASE_URL")

    ok = True

    if not db_url:
        print("ERROR: DATABASE_URL is not set")
        ok = False
    else:
        if not validate_database_url("DATABASE_URL", db_url):
            ok = False

    if not test_db_url:
        print("ERROR: TEST_DATABASE_URL is not set")
        ok = False
    else:
        if not validate_database_url("TEST_DATABASE_URL", test_db_url):
            ok = False

    # Check individual DB_* vars for obvious placeholders
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")

    if user and is_placeholder(user):
        print("ERROR: DB_USER is a placeholder or missing")
        ok = False
    if password and is_placeholder(password):
        print("ERROR: DB_PASSWORD is a placeholder or missing")
        ok = False
    if host and is_placeholder(host):
        print("ERROR: DB_HOST is a placeholder or missing")
        ok = False
    if name and is_placeholder(name):
        print("ERROR: DB_NAME is a placeholder or missing")
        ok = False

    if not ok:
        print("Secrets validation failed. Please set correct database secrets and try again.")
        return 2

    print("Secrets validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())