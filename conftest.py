
"""
Pytest boostrap

Key behaviors:
- Fixed BASE_URL (`https://reqres.in/api`) for simplicity.
- Injects the free API key header (`x-api-key: reqres-free-v1`) on every request.
- Disables proxies (session.trust_env = False) to avoid corporate/VPN proxy 401s.
"""
from __future__ import annotations
import requests
import pytest

BASE_URL = "https://reqres.in/api"
REQRES_API_KEY = "reqres-free-v1"   # free demo key from ReqRes

class API:
    """Tiny, explicit HTTP client for the tests.
    
    Exposes .get/.post/.put/.delete() and carries a configured Session so
    every request has the right headers and ignores proxy env vars.
    """
    def __init__(self, base: str, api_key: str) -> None:
        self.base = base.rstrip("/")
        self.session = requests.Session()
        # Ignore HTTP(S)_PROXY environment variables:
        self.session.trust_env = False
        # Always send the API key:
        self.session.headers.update({"x-api-key": api_key})

    def _u(self, path: str) -> str:
        return f"{self.base}/{path.lstrip('/')}"

    def get(self, path: str, **kw):    return self.session.get(self._u(path), **kw)
    def post(self, path: str, **kw):   return self.session.post(self._u(path), **kw)
    def put(self, path: str, **kw):    return self.session.put(self._u(path), **kw)
    def delete(self, path: str, **kw): return self.session.delete(self._u(path), **kw)

@pytest.fixture(scope="session")
def api() -> API:
    """Session-scoped API client used by tests."""
    return API(BASE_URL, REQRES_API_KEY)
