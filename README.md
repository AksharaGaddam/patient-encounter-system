# Medical Encounter Management System (MEMS)

Production-grade backend for managing patients, doctors, and appointments.

Features:
- FastAPI application in `src/main.py` ✅
- SQLAlchemy models under `src/models` (tables prefixed with `akshara_`) ✅
- Pydantic schemas under `src/schemas` with strong validation ✅
- Transactional appointment scheduling with conflict detection ✅

Database
- The project is configured to use a MySQL instance. Update `src/database.py` if needed.
- **Do not commit real credentials into the repository.** For CI, store credentials in GitHub Actions secrets (see below).


Table names:
- `akshara_patients`
- `akshara_doctors`
- `akshara_appointments`

Running locally
1. Install dependencies:
   pip install -r requirements.txt
2. Create a `.env` file from `.env.example` and edit it if necessary (the project defaults to the provided MySQL credentials):
   cp .env.example .env  # edit values if you want to use a different DB

3. To run migrations (recommended):
   python -m scripts.run_migrations

4. To seed sample data (local dev):
   python -m scripts.seed_data

5. To test DB connectivity:
   python -m scripts.test_connection

6. To create tables directly (not recommended for production):
   python -m src.create_tables

7. Start the app:
   uvicorn src.main:app --reload

7. Open API docs:
   http://127.0.0.1:8000/docs

Health check
- GET /health — checks DB connectivity and returns 200 if OK, 503 otherwise.

Notes
- When running integration tests or CI, the environment variable `TEST_DATABASE_URL` is used to point tests and migrations at the test DB (CI picks this up from GitHub Actions secrets).
- **Security**: Do not store credentials directly in the repository. Instead set the following **GitHub Actions secrets** in your repository settings (Settings → Secrets and variables → Actions):
  - `DATABASE_URL` — full DB connection string (preferred), e.g. `mysql+pymysql://user:pass@host:3306/dbname`
  - `TEST_DATABASE_URL` — used by integration tests (if different from `DATABASE_URL`)
  - Alternatively, set `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` as secrets and construct `DATABASE_URL` yourself.

Local validation
- A small validator is provided at `scripts/validate_secrets.py`. CI runs this early to ensure secrets are present and correctly formed.
- Run it locally to verify your `.env` or secrets before pushing:
  python -m scripts.validate_secrets

Example:

- `TEST_DATABASE_URL` = `mysql+pymysql://mems_user:changeme@127.0.0.1:3306/mems_db`

Note: Docker Compose integration was removed from CI and local workflows. Use a running MySQL instance and set `TEST_DATABASE_URL` appropriately.

Tip: Use the repository settings UI to add these values; they will be masked in logs and accessible only to Actions. You can also use organization secrets for shared projects.

Testing
- Run unit tests:
  pytest

CI
- A GitHub Actions pipeline is included at `.github/workflows/ci.yml` to run linting (ruff), formatting check (black), security checks (bandit), and tests (pytest).

Notes
- All datetimes are timezone-aware and validated on input.
- Appointment durations are limited to 15–180 minutes.
- Doctors must be active to receive appointments. Patients/doctors with existing appointments cannot be deleted.
