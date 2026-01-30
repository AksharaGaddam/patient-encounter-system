from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class PatientRead(PatientCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id")
    def id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("id must be a positive integer")
        return v

    class Config:
        orm_mode = True
