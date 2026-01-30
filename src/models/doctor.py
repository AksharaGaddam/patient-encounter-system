from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from src.database import Base

class Doctor(Base):
    __tablename__ = "akshara_doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    specialization = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
