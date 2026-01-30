"""Quick script to test DB connectivity using current environment variables.

Usage:
  python -m scripts.test_connection
"""
from src.database import engine

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            r = conn.execute("SELECT NOW()")
            print("Connected OK. Server time:", r.fetchone())
    except Exception as e:
        print("Connection failed:", e)
        raise
