CI notes:

- Integration job expects a reachable `TEST_DATABASE_URL` pointing to a running test database. Docker Compose steps were removed; provide a test database via repository secret or external service.
- **Secrets**: workflows read database connection strings from `DATABASE_URL` and `TEST_DATABASE_URL` repository secrets to avoid storing credentials in the repo.
- Migration autogenerate check: creates an autogenerate revision and fails the job if it causes the repository to have unstaged changes (models != migrations).
- Coverage is enforced at 80% via `--cov-fail-under=80`.
