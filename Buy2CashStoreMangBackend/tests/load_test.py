from locust import HttpUser, task, between

STORE_ID = "StoreIDHere"

class LoadTestingUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def test_query(self):
        payload = {"store_id": STORE_ID, "query": "top selling categories"}
        self.client.post("/query", json=payload)

    @task(2)
    def test_top_products(self):
        self.client.get(f"/api/analytics/top-selling-products/{STORE_ID}")

    @task(1)
    def test_health(self):
        self.client.get("/health")
