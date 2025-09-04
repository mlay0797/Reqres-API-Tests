# Reqres API Tests
[![CI](https://github.com/mlay0797/Reqres-API-Tests/actions/workflows/ci.yml/badge.svg)](https://github.com/mlay0797/Reqres-API-Tests/actions/workflows/ci.yml)

A small, readable **pytest** suite for the **Reqres** Users API.

## Highlights
- Sends the free API key automatically (`x-api-key: reqres-free-v1`)
- Disables proxies (`trust_env=False`) to avoid surprise 401s on corporate/VPN networks
- Covers **GET /users (pagination), GET /users/{id}, POST /users, PUT /users/{id}, DELETE /users/{id}**
- Negative & edge cases: 404 user, extra/missing fields on create, update non-existent user, double delete
- Optional lightweight **performance** checks (skipped by default in CI)

## Project Structure
```text
.
├─ conftest.py                  # api fixture + session config (API key, no proxies)
├─ tests/
│  ├─ test_users_api.py         # CRUD + negatives + pagination + optional perf
│  └─ schemas/
│     └─ user_list_schema.json  # JSON Schema for GET /users?page=n shape
├─ .github/workflows/ci.yml     # CI: runs core tests, uploads reports
├─ requirements.txt
├─ pytest.ini
└─ reports/                     # HTML/JUnit reports (artifact in CI)
```

## Setup & Run (macOS / Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p reports
pytest -m "not performance"   --junitxml=reports/junit.xml   --html=reports/report.html --self-contained-html

# Open the HTML report (macOS; use xdg-open on Linux)
open reports/report.html
```

### Enable perf checks (optional)
```bash
# Adjust if your network is slower
LATENCY_BUDGET_S=2.5 pytest -m performance   --html=reports/report_perf.html --self-contained-html
```

## Design & Reasoning
- **Contract first, then negatives.** Verify happy-path CRUD to establish the observed contract, then add targeted negatives/edges (404, extra/missing fields, non-existent update, double delete).
- **Schema over magic values.** Validate the **shape** of list responses with JSON Schema (draft-07) instead of hardcoding counts/IDs—this catches real regressions (missing/renamed fields, wrong types) without flaking on demo data.
- **Document mock quirks.** Reqres may echo unknown fields on POST, return `200` for PUT on non-existent, and `204` for repeated DELETEs. Tests accept and document that behavior.
- **Stable runs.** The suite injects the free API key and disables proxies so it runs cleanly on any machine/CI. Performance checks are lightweight and **opt-in** to avoid network flakiness on a public mock.

### Assumptions
- No official OpenAPI was provided, so I **derived** a minimal schema from live responses + docs examples.
- `additionalProperties: true` is kept in the schema to avoid overfitting to sample payloads.

## Test Output
The latest local run is committed under `docs/`:
- [HTML report](./docs/report.html) — download and open locally
- [JUnit XML](./docs/junit.xml)
- [Run info](./docs/REPORT_INFO.txt)

## CI
The workflow at `./.github/workflows/ci.yml` runs the core suite on Python **3.10** & **3.11**, caches pip, cancels stale runs, and uploads `reports/` as an artifact. Performance tests remain opt-in.
