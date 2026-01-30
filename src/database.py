import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")


from dotenv import load_dotenv

load_dotenv()

# Prefer TEST_DATABASE_URL for integration tests, then explicit DATABASE_URL, otherwise build from components
DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("DB_USER", "your_db_user")
    password = os.getenv("DB_PASSWORD", "changeme")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME", "your_db_name")
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")