from datetime import timedelta, datetime, timezone, time
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.appointment import Appointment
from src.models.patient import Patient
from src.models.doctor import Doctor


class AppointmentConflictError(Exception):
    """Raised when an appointment conflicts with an existing one."""


class AppointmentValidationError(Exception):
    """Raised when appointment data is invalid."""


def _ensure_aware(dt):
    if dt is None:
        return dt
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Assume naive stored datetimes are UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _overlaps(start_a, end_a, start_b, end_b):
    a0 = _ensure_aware(start_a)
    a1 = _ensure_aware(end_a)
    b0 = _ensure_aware(start_b)
    b1 = _ensure_aware(end_b)
    return (a0 < b1) and (a1 > b0)


def create_appointment(session: Session, *, patient_id: int, doctor_id: int, start_time: datetime, duration_minutes: int):
    # Enforce timezone-aware
    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        raise AppointmentValidationError("start_time must be timezone-aware")

    if duration_minutes < 15 or duration_minutes > 180:
        raise AppointmentValidationError("duration_minutes must be between 15 and 180")

    now = datetime.now(timezone.utc)
    if start_time <= now:
        raise AppointmentValidationError("appointments must be scheduled in the future")

    # Use nested transaction to be compatible with test sessions
    with session.begin_nested():

        patient = session.get(Patient, patient_id)
        if not patient:
            raise ValueError("patient not found")

        doctor = session.get(Doctor, doctor_id)
        if not doctor:
            raise ValueError("doctor not found")

        if not doctor.is_active:
            raise AppointmentValidationError("doctor is not active and cannot accept appointments")

        new_start = start_time
        new_end = new_start + timedelta(minutes=duration_minutes)

        # Lock appointments for this doctor to prevent race conditions
        existing_appointments = (
            session.query(Appointment)
            .filter(Appointment.doctor_id == doctor_id)
            .with_for_update()
            .all()
        )

        for appt in existing_appointments:
            appt_start = appt.start_time
            appt_end = appt_start + timedelta(minutes=appt.duration_minutes)
            if _overlaps(appt_start, appt_end, new_start, new_end):
                raise AppointmentConflictError("appointment conflicts with an existing appointment")

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_time=start_time,
            duration_minutes=duration_minutes,
        )

        session.add(appointment)
        session.flush()
        session.refresh(appointment)
        return appointment


def get_appointments_for_date(session: Session, date, doctor_id: int = None):
    # date: a datetime.date object; return appointments that start within that date (UTC)
    start_dt = datetime.combine(date, time.min).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(date, time.max).replace(tzinfo=timezone.utc)

    q = session.query(Appointment).filter(
        and_(Appointment.start_time >= start_dt, Appointment.start_time <= end_dt)
    )
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)
    return q.order_by(Appointment.start_time).all()
