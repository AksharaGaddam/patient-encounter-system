import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.database import Base
from src.models.patient import Patient


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_email_uniqueness(session):
    p1 = Patient(first_name="Alice", last_name="Smith", email="alice@example.com")
    session.add(p1)
    session.commit()

    p2 = Patient(first_name="Bob", last_name="Jones", email="alice@example.com")
    session.add(p2)
    with pytest.raises(IntegrityError):
        session.commit()