import requests
from .constants import API_URL

def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_states(token: str):
    r = requests.get(f"{API_URL}/states", headers=_headers(token), timeout=30)
    r.raise_for_status()
    return r.json()
