import requests

BASE_URL = "http://localhost:8000"
STORE_ID = "StoreIdHere"

queries = [
    {"store_id": STORE_ID, "query": "top selling products"},
    {"store_id": STORE_ID, "query": "unsold products"},
    {"store_id": STORE_ID, "query": "store performance"},
]

def test_regression_queries():
    for q in queries:
        res = requests.post(f"{BASE_URL}/query", json=q)
        assert res.status_code == 200
        data = res.json()
        assert "response" in data or "results" in data
