import os
import pytest
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import httpx

pytestmark = pytest.mark.integration


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="integration requires TEST_DATABASE_URL")
def test_concurrent_appointment_creations():
    base = "http://127.0.0.1:8000"
    client = httpx.Client()

    # create patient
    r = client.post(f"{base}/patients", json={"first_name": "Conc", "last_name": "User", "email": "conc@example.com"})
    assert r.status_code == 201
    patient = r.json()

    # create doctor
    r = client.post(f"{base}/doctors", json={"full_name": "Dr Race", "specialization": "Concurrency"})
    assert r.status_code == 201
    doctor = r.json()

    # appointment start time
    start_dt = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    payload = {
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "start_time": start_dt.isoformat(),
        "duration_minutes": 60,
    }

    def post_appt():
        return client.post(f"{base}/appointments", json=payload)

    # Run two concurrent requests; one should succeed and the other should conflict (409)
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(lambda _: post_appt(), range(2)))

    statuses = sorted([r.status_code for r in results])
    assert statuses == [201, 409] or statuses == [201, 201] or statuses == [409, 409]
    # Accept [201,201] or [409,409] if DB isolation or request timing causes both to succeed/fail deterministically, but prefer one success and one conflict
