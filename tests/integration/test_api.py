import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from src.main import app


pytestmark = pytest.mark.integration


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="integration tests require TEST_DATABASE_URL")
def test_full_flow_and_conflicts():
    client = TestClient(app)

    # Create patient
    r = client.post("/patients", json={
        "first_name": "Integration",
        "last_name": "Tester",
        "email": "integration@example.com"
    })
    assert r.status_code == 201
    patient = r.json()

    # Create doctor
    r = client.post("/doctors", json={
        "full_name": "Dr Integration",
        "specialization": "Testing"
    })
    assert r.status_code == 201
    doctor = r.json()

    # Schedule appointment 1 day from now at 10:00 UTC
    start_dt = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    start_iso = start_dt.isoformat()

    r = client.post("/appointments", json={
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "start_time": start_iso,
        "duration_minutes": 30
    })
    assert r.status_code == 201

    # Attempt overlapping appointment -> should return 409
    r = client.post("/appointments", json={
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "start_time": start_iso,
        "duration_minutes": 30
    })
    assert r.status_code == 409

    # Query appointments for the date
    date_str = start_dt.date().isoformat()
    r = client.get(f"/appointments?date={date_str}&doctor_id={doctor['id']}")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Deleting doctor with existing appointments should be blocked
    r = client.delete(f"/doctors/{doctor['id']}")
    assert r.status_code == 400
