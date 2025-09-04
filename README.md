# Reqres API Tests
[![CI](https://github.com/mlay0797/Reqres-API-Tests/actions/workflows/ci.yml/badge.svg)](https://github.com/mlay0797/Reqres-API-Tests/actions/workflows/ci.yml)

A **pytest** suite for the **Reqres** Users API.

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
## Test Strategy
- **CRUD Coverage:** Validated create, read, update, and delete flows against Reqres API docs.  
- **Negative Cases:** Checked invalid IDs, malformed payloads, and unsupported methods to confirm error handling.  
- **Schema Validation:** Enforced response structure and types with JSON Schema (user object and user list).  
- **Pagination & Lists:** Verified paging mechanics and list shapes beyond single-record CRUD.  
- **Performance (Opt-in):** Added simple latency checks with a default budget (2.5s), disabled by default to avoid flakiness.  

## Design & Reasoning
- **Contract First Approach:** Began with the “happy path” to define the observed API contract, then layered negatives and edge cases for depth.  
- **Choosing JSON Schema:** Reqres docs provide only sample payloads, so I derived the schema manually by analyzing example responses (fields, types, required vs optional). I used JSON Schema draft-07 to formalize this contract, ensuring responses are validated structurally rather than by brittle value checks.  
- **Schema over Hardcoding:** Chose schema validation over asserting on specific counts or IDs, catching meaningful regressions (missing/renamed fields, wrong types) without false failures on demo data.  
- **Mock API Awareness:** Documented quirks (e.g., POST echoes extra fields, PUT returns `200` on non-existent records, repeated DELETEs return `204`) so tests reflect real Reqres behavior.  
- **Stable & Portable Runs:** Disabled proxies, added API key injection, and kept perf checks opt-in to ensure reproducibility in CI or local runs.  
- **Readable by Design:** Optimized for clarity and demonstration value rather than raw coverage volume.

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
