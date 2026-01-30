from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.database import SessionLocal
from src.schemas import patient as patient_schema
from src.schemas import doctor as doctor_schema
from src.schemas import appointment as appointment_schema
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from src.services.appointment_service import (
    create_appointment,
    AppointmentConflictError,
    AppointmentValidationError,
    get_appointments_for_date,
)

app = FastAPI(title="Patient Encounter System")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health(db = Depends(get_db)):
    """Simple health endpoint that checks DB connectivity."""
    from src.database import engine
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.exception_handler(AppointmentConflictError)
def handle_conflict(request, exc: AppointmentConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(AppointmentValidationError)
def handle_validation(request, exc: AppointmentValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Patients
@app.post("/patients", response_model=patient_schema.PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(payload: patient_schema.PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**payload.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/patients/{patient_id}", response_model=patient_schema.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="patient not found")
    return patient


@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    # Prevent deletion if patient has appointments
    existing = db.query(Appointment).filter(Appointment.patient_id == patient_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="patient has existing appointments and cannot be deleted")
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="patient not found")
    db.delete(patient)
    db.commit()
    return JSONResponse(status_code=204, content=None)


# Doctors
@app.post("/doctors", response_model=doctor_schema.DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: doctor_schema.DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(**payload.dict())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@app.get("/doctors/{doctor_id}", response_model=doctor_schema.DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="doctor not found")
    return doctor


@app.patch("/doctors/{doctor_id}", response_model=doctor_schema.DoctorRead)
def update_doctor_status(doctor_id: int, payload: doctor_schema.DoctorUpdate, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="doctor not found")
    doctor.is_active = payload.is_active
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@app.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    existing = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="doctor has existing appointments and cannot be deleted")
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="doctor not found")
    db.delete(doctor)
    db.commit()
    return JSONResponse(status_code=204, content=None)


# Appointments
@app.post("/appointments", response_model=appointment_schema.AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_new_appointment(payload: appointment_schema.AppointmentCreate, db: Session = Depends(get_db)):
    appt = create_appointment(
        session=db,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        start_time=payload.start_time,
        duration_minutes=payload.duration_minutes,
    )
    return appt


@app.get("/appointments", response_model=list[appointment_schema.AppointmentRead])
def list_appointments(date: date, doctor_id: Optional[int] = None, db: Session = Depends(get_db)):
    appointments = get_appointments_for_date(db, date, doctor_id)
    return appointments
