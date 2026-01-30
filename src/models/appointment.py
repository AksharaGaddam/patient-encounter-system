from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime, timezone
from src.database import Base

class Appointment(Base):
    __tablename__ = "akshara_appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("akshara_patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("akshara_doctors.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), index=True, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))