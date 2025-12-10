import requests

BASE_URL = "http://localhost:8000"
STORE_ID = "StoreIdHere"

def test_user_journey():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200

    res = requests.get(f"{BASE_URL}/api/stores")
    assert res.status_code == 200
    stores = res.json()["stores"]
    assert len(stores) > 0
    store_id = stores[0]["store_id"]

    payload = {"store_id": store_id, "query": "top selling snacks"}  
    res = requests.post(f"{BASE_URL}/query", json=payload)
    assert res.status_code == 200
    session = res.json()
    assert "session_id" in session
    session_id = session["session_id"]

    res = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    assert res.status_code in [200, 404]
