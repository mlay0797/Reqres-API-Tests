
""""ReqRes Users API tests (CRUD)

What we validate (contract-first):
- List & pagination behave consistently across pages.
- Data shape via JSON Schema (catches over/under-return without hardcoding values).
- Happy paths for GET/POST/PUT/DELETE.
- High-value negatives & edge cases:
  * GET /users/{id} 404 for missing user (body may be empty on this mock)
  * POST with extra/missing fields (mock may echo unknown fields)
  * PUT on non-existent user still returns 200 with updatedAt (documented quirk)
  * DELETE twice returns 204 both times (idempotent-like on this mock)

Perf note:
- Optional latency checks are marked @pytest.mark.performance and are skipped by default in CI
  to avoid flakiness on public networks.
"""

import os
import pytest
from jsonschema import validate
from requests import Response

# Configurable latency budget (only for running performance-marked tests)
LATENCY_BUDGET_S = float(os.getenv("LATENCY_BUDGET_S", "2.0"))

def assert_latency_under(resp: Response, budget: float = LATENCY_BUDGET_S) -> None:
    elapsed = resp.elapsed.total_seconds()
    assert elapsed < budget, f"Response took {elapsed:.3f}s which exceeds {budget:.3f}s"

def load_schema(name: str) -> dict:
    """Load a JSON schema from tests/schemas/"""
    import json, pathlib
    path = pathlib.Path(__file__).parent / "schemas" / name
    return json.loads(path.read_text())

@pytest.mark.parametrize("page", [1, 2]) # run the same contract checks on multiple pages
def test_list_users_matches_schema_and_paginates(api, page):
    """GET /users?page=n returns proper pagination fields and matches shape."""
    r = api.get("/users", params={"page": page})
    assert r.status_code == 200, f"Unexpected status {r.status_code} body={r.text!r}"
    body = r.json()
    validate(instance=body, schema=load_schema("user_list_schema.json"))
    assert body["page"] == page
    assert len(body["data"]) <= body["per_page"]

def test_list_users_pages_are_distinct(api):     # Different pages should not be identical; catches broken pagination backends
    """Different pages should not contain identical data arrays."""
    r1 = api.get("/users", params={"page": 1})
    r2 = api.get("/users", params={"page": 2})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["data"] != r2.json()["data"]

def test_get_user_by_id_success(api):
    """GET /users/{id} returns expected fields for a known id."""
    r = api.get("/users/2")
    assert r.status_code == 200
    d = r.json()["data"]
    for k in ("id","email","first_name","last_name","avatar"):
        assert k in d
    assert d["id"] == 2

def test_get_user_not_found(api):    # ReqRes returns 404; body may be "" or {} — accept either to align with the mock
    """GET /users/{id} returns 404 for a non-existent id (empty body allowed)."""
    r = api.get("/users/23")
    assert r.status_code == 404
    assert r.text == "" or r.json() == {}

def test_post_create_user_happy_path(api):
    """POST /users echoes core fields and returns id + createdAt."""
    payload = {"name": "Matthew", "job": "QA Engineer"}
    r = api.post("/users", json=payload)
    assert r.status_code == 201, f"Unexpected status {r.status_code} body={r.text!r}"
    b = r.json()
    assert b.get("name") == "Matthew" and b.get("job") == "QA Engineer"
    assert "id" in b and "createdAt" in b

def test_post_create_user_with_extra_field(api):
    """POST /users with extra field: API may echo or ignore unknown fields; document either."""
    payload = {"name": "Alice", "job": "SDET", "admin": True}
    r = api.post("/users", json=payload)
    assert r.status_code == 201
    b = r.json()
    # Core guarantees:
    assert "id" in b and "createdAt" in b and b.get("name") == "Alice"
    # If API echoes extras, ensure the value matches our request:
    if "admin" in b:
        assert b["admin"] is True

def test_post_missing_optional_field(api):
    """POST /users with only 'name' still succeeds on this mock."""
    r = api.post("/users", json={"name": "Matthew"})
    assert r.status_code == 201
    b = r.json()
    assert b.get("name") == "Matthew"
    assert "job" not in b  # Not required by the mock

def test_put_update_user(api):
    """PUT /users/{id} echoes updated fields and returns updatedAt."""
    r = api.put("/users/2", json={"name": "Matthew", "job": "Senior QA"})
    assert r.status_code == 200
    b = r.json()
    assert b.get("name") == "Matthew" and b.get("job") == "Senior QA"
    assert "updatedAt" in b

def test_put_nonexistent_user_observed_behavior(api):
    """PUT to a non-existent id still returns 200 on ReqRes; we assert/document that behavior."""
    r = api.put("/users/9999", json={"name": "Ghost", "job": "Unknown"})
    assert r.status_code == 200
    assert "updatedAt" in r.json()

def test_delete_user_twice_is_idempotent_like(api): 
    """DELETE returns 204; repeating the call also returns 204 on this mock."""
    r1 = api.delete("/users/2")
    assert r1.status_code == 204
    r2 = api.delete("/users/2")
    assert r2.status_code == 204

# --- Optional performance checks (excluded in CI) ---
@pytest.mark.performance
def test_latency_threshold_on_list_users(api):
    r = api.get("/users", params={"page": 2})
    assert_latency_under(r)

@pytest.mark.performance
def test_small_burst_stays_under_budget(api):
    lat = []
    for _ in range(10):
        r = api.get("/users", params={"page": 1})
        assert r.status_code == 200
        lat.append(r.elapsed.total_seconds())
    assert max(lat) < LATENCY_BUDGET_S, f"Max latency {max(lat):.3f}s >= {LATENCY_BUDGET_S:.3f}s"
