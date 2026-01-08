// api.ts - API Functions and Utilities

const STORE_ID = "68d11731a79f004f440c31a2";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

// Helper function to build query params
const buildQueryParams = (params: Record<string, any>): URLSearchParams => {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      queryParams.append(key, String(value));
    }
  });
  return queryParams;
};

// API Functions
export async function fetchTotalProducts(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/total-products/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTotalSales(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/total-sales/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTotalRevenue(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/total-revenue/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchAvgOrderValue(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/avg-order-value/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTotalCustomers(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/total-customers/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchUniqueCustomers(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/unique-customers/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTopCustomers(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/top-customers/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTopStockAlerts(storeId: string) {
  const url =
    `${API_BASE}/api/analytics/top-stock-alerts/${storeId}` +
    `?ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchQuickAnalysis(storeId: string) {
  const url =
    `${API_BASE}/api/analytics/quick-analysis/${storeId}` +
    `?ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchMonthlyRevenue(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/monthly-revenue/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchProductsByCategory(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/products-by-category/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchRecentOrders(storeId: string, query = {}) {
  const params = buildQueryParams(query);
  const url =
    `${API_BASE}/api/analytics/recent-orders/${storeId}` +
    `?${params}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTopDishSearches(storeId: string) {
  const url =
    `${API_BASE}/api/analytics/top-dish-searches/${storeId}` +
    `?ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function fetchTopSellingProducts(storeId: string, params = {}) {
  const queryParams = buildQueryParams(params);
  const url =
    `${API_BASE}/api/analytics/top-selling-products/${storeId}` +
    `?${queryParams}&ngrok-skip-browser-warning=true`;

  const res = await fetch(url);

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    throw new Error(await res.text());
  }

  return res.json();
}

// Helper Functions
export const aggregateDishSearches = (dishQueryData: any[]) => {
  const dishCounts: Record<string, number> = {};
  
  dishQueryData.forEach(item => {
    if (item.dishbased && Array.isArray(item.dishbased)) {
      item.dishbased.forEach((dish: string) => {
        if (dish) {
          dishCounts[dish] = (dishCounts[dish] || 0) + 1;
        }
      });
    }
  });
  
  return Object.entries(dishCounts)
    .map(([name, count]) => ({ name, searches: count }))
    .sort((a, b) => b.searches - a.searches)
    .slice(0, 5);
};

export const aggregateIngredientDemand = (dishQueryData: any[]) => {
  const ingredientCounts: Record<string, number> = {};
  
  dishQueryData.forEach(item => {
    if (item.product_name && Array.isArray(item.product_name)) {
      item.product_name.forEach((product: string) => {
        if (product) {
          ingredientCounts[product] = (ingredientCounts[product] || 0) + 1;
        }
      });
    }
  });
  
  return Object.entries(ingredientCounts)
    .map(([name, queries]) => ({ name, queries }))
    .sort((a, b) => b.queries - a.queries)
    .slice(0, 5);
};

// Utility Functions
export const formatCurrency = (value: number) => {
  if (value === null || value === undefined) return '₹0';
  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)}L`;
  } else if (value >= 1000) {
    return `₹${(value / 1000).toFixed(1)}K`;
  }
  return `₹${value.toFixed(0)}`;
};

export const formatNumber = (value: number) => {
  if (value === null || value === undefined) return '0';
  return value.toLocaleString();
};

export const formatDateTime = (dateTimeStr: string) => {
  if (!dateTimeStr) return 'N/A';
  try {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-IN', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  } catch (err) {
    return dateTimeStr;
  }
};

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'COMPLETED':
      return 'bg-green-100 text-green-700';
    case 'PENDING':
    case 'ACCEPTED':
      return 'bg-yellow-100 text-yellow-700';
    case 'IN_DELIVERY':
    case 'PICKED_UP':
      return 'bg-blue-100 text-blue-700';
    case 'CANCELLED':
    case 'EXPIRED':
      return 'bg-red-100 text-red-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export const formatStatus = (status: string) => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const formatTimestamp = (timestamp: string) => {
  if (!timestamp) return 'N/A';
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  } catch (err) {
    return timestamp;
  }
};

export const getDemandLevel = (productCount: number) => {
  if (!productCount || productCount === 0) return 'Low';
  if (productCount >= 30) return 'High';
  if (productCount >= 15) return 'Medium';
  return 'Low';
};

export const categoryColors = [
  '#1E1B4B', '#4338CA', '#818CF8','#FDB022', 
  '#10B981', '#EC4899', '#EF4444', '#14B8A6'
];

export { STORE_ID };