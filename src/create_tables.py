from src.database import engine, Base
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment

Base.metadata.create_all(bind=engine)
