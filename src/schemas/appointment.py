from pydantic import BaseModel, validator
from datetime import datetime, timezone


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int

    @validator("start_time")
    def must_be_timezone_aware(cls, v: datetime):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("start_time must be timezone-aware")
        return v

    @validator("duration_minutes")
    def duration_bounds(cls, v: int):
        if not (15 <= v <= 180):
            raise ValueError("duration_minutes must be between 15 and 180")
        return v


class AppointmentRead(AppointmentCreate):
    id: int
    created_at: datetime

    @validator("id")
    def id_positive(cls, v):
        if v <= 0:
            raise ValueError("id must be a positive integer")
        return v

    class Config:
        orm_mode = True
