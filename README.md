
# ReqRes API Tests

A small, readable **pytest** suite for the **ReqRes** Users API.
- Always sends the free API key (`x-api-key: reqres-free-v1`)
- Disables proxies (`trust_env=False`) to avoid surprise 401s
- Covers **GET/POST/PUT/DELETE**, negatives, pagination, and schema checks
- Includes optional lightweight **performance** tests (skipped by default in CI)

## Setup & Run (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p reports
pytest -m "not performance"   --junitxml=reports/junit.xml   --html=reports/report.html --self-contained-html

# Open the HTML report
open reports/report.html  # macOS; use 'xdg-open' on Linux
```

### Enable perf checks (optional)
```bash
LATENCY_BUDGET_S=2.5 pytest -m performance   --html=reports/report_perf.html --self-contained-html
```

## Design & Reasoning

- **Contract first, then negatives.** Start with happy-path CRUD to lock the observed contract, then add high‑value negatives (404 user, update non‑existent, double delete) and edge cases (missing/extra fields).
- **Schema over magic values.** Use JSON Schema to catch over/under‑return without hardcoding specific values.
- **Stable** The suite injects the free ReqRes API key and disables proxies so it runs cleanly on any machine/CI.
- **Performance is light.** A tiny latency guard is included but kept optional to avoid network flakiness; CI skips it by default.

## CI
A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It installs deps, runs tests **excluding** perf, and uploads `reports/` as an artifact.
