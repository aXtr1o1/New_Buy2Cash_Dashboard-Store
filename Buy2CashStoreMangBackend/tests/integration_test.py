import requests

BASE_URL = "http://localhost:8000"
STORE_ID = "store_id_here"  
def test_store_workflow():
    res = requests.get(f"{BASE_URL}/api/stores")
    assert res.status_code == 200
    stores = res.json()["stores"]
    assert len(stores) > 0

    store_id = stores[0]["store_id"]

    res = requests.get(f"{BASE_URL}/api/analytics/top-selling-products/{store_id}")
    assert res.status_code == 200
    assert isinstance(res.json()["top_selling_products"], list)

    res = requests.get(f"{BASE_URL}/api/analytics/store-performance/{store_id}")
    assert res.status_code == 200
    data = res.json()
    assert "performance_metrics" in data
    assert "store_info" in data
