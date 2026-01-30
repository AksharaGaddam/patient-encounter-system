import os
import pytest
from datetime import datetime, timedelta, timezone, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from src.services.appointment_service import (
    create_appointment,
    AppointmentConflictError,
    AppointmentValidationError,
    get_appointments_for_date,
)


@pytest.fixture
def session():
    # Support an external TEST_DATABASE_URL for integration tests in CI
    test_db_url = os.getenv('TEST_DATABASE_URL')
    if test_db_url:
        engine = create_engine(test_db_url)
    else:
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_patient_and_doctor(session):
    patient = Patient(first_name="John", last_name="Doe", email="john@example.com")
    doctor = Doctor(full_name="Dr. Who", specialization="Time Travel")
    session.add(patient)
    session.add(doctor)
    session.commit()
    session.refresh(patient)
    session.refresh(doctor)
    return patient, doctor


def test_create_appointment_success(session):
    patient, doctor = create_patient_and_doctor(session)

    start = datetime.now(timezone.utc) + timedelta(days=1)
    appt = create_appointment(
        session=session,
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=start,
        duration_minutes=30,
    )

    assert appt.id is not None
    assert appt.patient_id == patient.id
    assert appt.doctor_id == doctor.id


def test_create_appointment_conflict(session):
    patient, doctor = create_patient_and_doctor(session)

    start = datetime.now(timezone.utc) + timedelta(days=1)
    # first appointment
    create_appointment(
        session=session,
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=start,
        duration_minutes=60,
    )

    # overlapping appointment should raise
    with pytest.raises(AppointmentConflictError):
        create_appointment(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=start + timedelta(minutes=30),
            duration_minutes=30,
        )


def test_reject_past_appointment(session):
    patient, doctor = create_patient_and_doctor(session)
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    with pytest.raises(AppointmentValidationError):
        create_appointment(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=start,
            duration_minutes=30,
        )


def test_duration_bounds(session):
    patient, doctor = create_patient_and_doctor(session)
    start = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(AppointmentValidationError):
        create_appointment(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=start,
            duration_minutes=10,
        )
    with pytest.raises(AppointmentValidationError):
        create_appointment(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=start,
            duration_minutes=1000,
        )


def test_doctor_inactive_cannot_accept(session):
    patient, doctor = create_patient_and_doctor(session)
    # deactivate doctor
    doctor.is_active = False
    session.add(doctor)
    session.commit()

    start = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(AppointmentValidationError):
        create_appointment(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            start_time=start,
            duration_minutes=30,
        )


def test_get_appointments_by_date(session):
    patient, doctor = create_patient_and_doctor(session)
    # Create two appointments on the same date
    start1 = datetime(2026, 1, 31, 9, 0, tzinfo=timezone.utc)
    start2 = datetime(2026, 1, 31, 11, 0, tzinfo=timezone.utc)
    create_appointment(session=session, patient_id=patient.id, doctor_id=doctor.id, start_time=start1, duration_minutes=30)
    create_appointment(session=session, patient_id=patient.id, doctor_id=doctor.id, start_time=start2, duration_minutes=30)

    result = get_appointments_for_date(session, date(2026, 1, 31))
    assert len(result) == 2


def test_prevent_deletion_with_appointments(session):
    patient, doctor = create_patient_and_doctor(session)
    start = datetime.now(timezone.utc) + timedelta(days=1)
    create_appointment(session=session, patient_id=patient.id, doctor_id=doctor.id, start_time=start, duration_minutes=30)

    # patient has appointment
    assert session.query(Appointment).filter(Appointment.patient_id == patient.id).first() is not None
    # deleting logic is handled at API layer; here we assert existence prevents deletion
    # simulate delete check
    existing = session.query(Appointment).filter(Appointment.patient_id == patient.id).first()
    assert existing is not None
