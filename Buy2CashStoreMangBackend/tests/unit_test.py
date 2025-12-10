import requests

BASE_URL = "http://localhost:8000"
STORE_ID = "StoreIdHere"
PRODUCT_ID = "ProductIdHere"
SESSION_ID = "SessionIdHere"

def test_health_check():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    assert "status" in res.json()

def test_get_stores():
    res = requests.get(f"{BASE_URL}/api/stores")
    assert res.status_code == 200
    data = res.json()
    assert "stores" in data
    assert isinstance(data["stores"], list)
    assert len(data["stores"]) > 0

def test_top_selling_products():
    res = requests.get(f"{BASE_URL}/api/analytics/top-selling-products/{STORE_ID}")
    assert res.status_code == 200

def test_popular_searches():
    res = requests.get(f"{BASE_URL}/api/analytics/popular-searches/{STORE_ID}")
    assert res.status_code == 200

def test_top_selling_categories():
    res = requests.get(f"{BASE_URL}/api/analytics/top-selling-categories/{STORE_ID}")
    assert res.status_code == 200

def test_unsold_products():
    res = requests.get(f"{BASE_URL}/api/analytics/unsold-products/{STORE_ID}")
    assert res.status_code == 200

def test_store_performance():
    res = requests.get(f"{BASE_URL}/api/analytics/store-performance/{STORE_ID}")
    assert res.status_code == 200

def test_query_endpoint():
    payload = {"store_id": STORE_ID, "query": "top selling products"}
    res = requests.post(f"{BASE_URL}/query", json=payload)
    assert res.status_code == 200

def test_sessions():
    res = requests.get(f"{BASE_URL}/api/sessions")
    assert res.status_code == 200

def test_session_by_id():
    res = requests.get(f"{BASE_URL}/api/sessions/{SESSION_ID}")
    assert res.status_code in [200, 404] 

def test_product_substitutions():
    res = requests.get(f"{BASE_URL}/stores/{STORE_ID}/products/{PRODUCT_ID}/substitutions")
    assert res.status_code in [200, 404]

def test_discount_recommendations():
    res = requests.get(f"{BASE_URL}/stores/{STORE_ID}/recommendations/discounts")
    assert res.status_code == 200
