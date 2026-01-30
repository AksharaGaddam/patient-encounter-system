"""Seed minimal data for local development: adds a few doctors and patients if they don't exist."""
from src.database import SessionLocal
from src.models.doctor import Doctor
from src.models.patient import Patient


def run():
    db = SessionLocal()
    try:
        if db.query(Doctor).count() == 0:
            docs = [
                Doctor(full_name="Dr. Alice", specialization="General Medicine"),
                Doctor(full_name="Dr. Bob", specialization="Pediatrics"),
            ]
            db.add_all(docs)
            print("Seeded doctors")

        if db.query(Patient).count() == 0:
            pats = [
                Patient(first_name="John", last_name="Doe", email="johndoe@example.com"),
                Patient(first_name="Jane", last_name="Doe", email="janedoe@example.com"),
            ]
            db.add_all(pats)
            print("Seeded patients")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Seeding complete")
