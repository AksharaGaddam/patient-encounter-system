from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class DoctorCreate(BaseModel):
    full_name: str
    specialization: Optional[str] = None


class DoctorRead(DoctorCreate):
    id: int
    is_active: bool
    created_at: datetime

    @validator("id")
    def id_positive(cls, v):
        if v <= 0:
            raise ValueError("id must be a positive integer")
        return v

    class Config:
        orm_mode = True


class DoctorUpdate(BaseModel):
    is_active: bool
