export const API_BASE = "http://localhost:8000";

// ─────────────────────────────────────────
// STORES  (BACKEND CURRENTLY COMMENTED OUT)
// ─────────────────────────────────────────
// If you re-enable /api/stores on the backend, you can use this.
// export async function fetchStores() {
//   const res = await fetch(`${API_BASE}/api/stores`);
//   return res.json();
// }

// ─────────────────────────────────────────
// ANALYTICS – EXISTING ENDPOINTS
// ─────────────────────────────────────────
export async function fetchTopProducts(storeId, limit = 10, period = 30) {
  const res = await fetch(
    `${API_BASE}/api/analytics/top-selling-products/${storeId}?limit=${limit}&period=${period}`
  );
  return res.json();
}

export async function fetchLowSellingProducts(storeId, limit = 10, period = 30) {
  const res = await fetch(
    `${API_BASE}/api/analytics/get_low_selling_products/${storeId}?limit=${limit}&period=${period}`
  );
  return res.json();
}

export async function fetchTopSellingCategories(storeId, period = 30) {
  const res = await fetch(
    `${API_BASE}/api/analytics/top-selling-categories/${storeId}?period=${period}`
  );
  return res.json();
}

export async function fetchUnsoldProducts(storeId, days = 30) {
  const res = await fetch(
    `${API_BASE}/api/analytics/unsold-products/${storeId}?days=${days}`
  );
  return res.json();
}

export async function fetchStorePerformance(storeId, period = 30) {
  const res = await fetch(
    `${API_BASE}/api/analytics/store-performance/${storeId}?period=${period}`
  );
  return res.json();
}

// ─────────────────────────────────────────
// ANALYTICS – NEW KPIs YOU ADDED
// ─────────────────────────────────────────

// total products
export async function fetchTotalProducts(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/total-products/${storeId}`
  );
  return res.json();
}

// return 

// total completed orders (sales count)
export async function fetchTotalSales(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/total-sales/${storeId}`
  );
  return res.json();
}

// total revenue (sum of `total`)
export async function fetchTotalRevenue(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/total-revenue/${storeId}`
  );
  return res.json();
}

// monthly revenue aggregation
export async function fetchMonthlyRevenue(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/monthly-revenue/${storeId}`
  );
  return res.json();
}

// total customers (currently = completed orders count)
export async function fetchTotalCustomers(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/total-customers/${storeId}`
  );
  return res.json();
}

// unique customers (based on customer.id)
export async function fetchUniqueCustomers(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/unique-customers/${storeId}`
  );
  return res.json();
}

// sales by time period (Morning/Afternoon/Evening/Night)
export async function fetchSalesByTimePeriod(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/sales-by-time-period/${storeId}`
  );
  return res.json();
}

// recent orders with filters + pagination
export async function fetchRecentOrders(
  storeId,
  {
    page = 1,
    limit = 10,
    status = null,
    orderType = null,
    dateFrom = null,
    dateTo = null,
  } = {}
) {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("limit", String(limit));

  if (status) params.set("status", status);
  if (orderType) params.set("order_type", orderType);
  if (dateFrom) params.set("date_from", dateFrom); // ISO string expected
  if (dateTo) params.set("date_to", dateTo);       // ISO string expected

  const res = await fetch(
    `${API_BASE}/api/analytics/recent-orders/${storeId}?${params.toString()}`
  );
  return res.json();
}

// Top Dish Searches (Supabase-powered)
export async function fetchTopDishSearches(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/Top_Dish_Searches/${storeId}`
  );
  return res.json();
}

// Top stock alerts + AI recommendations
export async function fetchTopStockAlerts(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/top-stock-alerts/${storeId}`
  );
  return res.json();
}

// ─────────────────────────────────────────
// AI FEATURES
// ─────────────────────────────────────────

// NOTE: backend path = /stores/{store_id}/products/substitutions?top_n=...
// It does NOT take productId in the URL; it uses low_stock products internally.
export async function fetchProductSubstitutions(storeId, topN = 5) {
  const res = await fetch(
    `${API_BASE}/stores/${storeId}/products/substitutions?top_n=${topN}`
  );
  return res.json();
}

