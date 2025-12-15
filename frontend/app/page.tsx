
'use client';
import React, { useState, useEffect } from 'react';
import { BarChart3, Package, Users, ShoppingCart, TrendingUp, Bell, Search, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';
// Store ID constant
const STORE_ID = "68d11731a79f004f440c31a2";
const API_BASE = "http://localhost:8000";

// API functions
async function fetchTotalProducts(storeId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/api/analytics/total-products/${storeId}?${queryParams.toString()}`);
  return res.json();
}

async function fetchTotalSales(storeId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/api/analytics/total-sales/${storeId}?${queryParams.toString()}`);
  return res.json();
}

async function fetchTotalRevenue(storeId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/api/analytics/total-revenue/${storeId}?${queryParams.toString()}`);
  return res.json();
}

async function fetchTotalCustomers(storeId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/api/analytics/total-customers/${storeId}?${queryParams.toString()}`);
  return res.json();
}

async function fetchUniqueCustomers(storeId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/api/analytics/unique-customers/${storeId}?${queryParams.toString()}`);
  return res.json();
}

async function fetchProductSubstitutions(storeId, topN = 5) {
  const res = await fetch(`${API_BASE}/stores/${storeId}/products/substitutions?top_n=${topN}`);
  return res.json();
}

async function fetchTopStockAlerts(storeId) {
  const res = await fetch(`${API_BASE}/api/analytics/top-stock-alerts/${storeId}`);
  return res.json();
}

async function fetchMonthlyRevenue(storeId) {
  const res = await fetch(`${API_BASE}/api/analytics/monthly-revenue/${storeId}`);
  return res.json();
}

async function fetchTopSellingCategories(storeId, period = 30) {
  const res = await fetch(`${API_BASE}/api/analytics/top-selling-categories/${storeId}?period=${period}`);
  return res.json();
}

async function fetchRecentOrders(storeId, query = {}) {
  const params = new URLSearchParams(query);
  const res = await fetch(
    `${API_BASE}/api/analytics/recent-orders/${storeId}?${params.toString()}`
  );
  return res.json();
}

async function fetchTopDishSearches(storeId) {
  const res = await fetch(
    `${API_BASE}/api/analytics/Top_Dish_Searches/${storeId}`
  );
  return res.json();
}

// Helper function to aggregate dish searches
const aggregateDishSearches = (dishQueryData) => {
  const dishCounts = {};
  
  dishQueryData.forEach(item => {
    if (item.dishbased && Array.isArray(item.dishbased)) {
      item.dishbased.forEach(dish => {
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

// Helper function to aggregate ingredient demand
const aggregateIngredientDemand = (dishQueryData) => {
  const ingredientCounts = {};
  
  dishQueryData.forEach(item => {
    if (item.product_name && Array.isArray(item.product_name)) {
      item.product_name.forEach(product => {
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

export default function Buy2CashDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [substitutionsLoading, setSubstitutionsLoading] = useState(false);
  
  // KPI States
  const [totalProducts, setTotalProducts] = useState(null);
  const [totalSales, setTotalSales] = useState(null);
  const [totalRevenue, setTotalRevenue] = useState(null);
  const [averageValue, setAverageValue] = useState(null);
  const [totalCustomers, setTotalCustomers] = useState(null);
  const [uniqueCustomers, setUniqueCustomers] = useState(null);
  
  // Product Substitutions State
  const [productSubstitutions, setProductSubstitutions] = useState([]);
  const [expandedProducts, setExpandedProducts] = useState({});
  
  // AI-Powered Analysis State
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  
  // Monthly Revenue State
  const [monthlyRevenue, setMonthlyRevenue] = useState([]);
  const [revenueLoading, setRevenueLoading] = useState(true);
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [hoveredSegment, setHoveredSegment] = useState(null);
  
  // Category Distribution State
  const [topCategories, setTopCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Recent Orders State
  const [recentOrders, setRecentOrders] = useState([]);
  const [ordersLoading, setOrdersLoading] = useState(true);
  const [ordersPagination, setOrdersPagination] = useState(null);
  const [ordersPerPage, setOrdersPerPage] = useState(5); // Start with 5
  const [currentPage, setCurrentPage] = useState(1);  

  // Dish Query Data State
  const [dishQueryData, setDishQueryData] = useState([]);
  const [dishQueriesLoading, setDishQueriesLoading] = useState(true);

  // Filter States
  const [filterPeriod, setFilterPeriod] = useState('30');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchText, setSearchText] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);


  //

  // Fetch all KPI data
  useEffect(() => {
    const fetchAllKPIs = async () => {
      try {
        setLoading(true);
        setError(null);

        // Build query parameters
        const params = {};
        if (filterStatus !== 'all') {
          params.status = filterStatus;
        }
        if (dateFrom) {
          params.date_from = dateFrom;
        }
        if (dateTo) {
          params.date_to = dateTo;
        }

        const [
          productsData,
          salesData,
          revenueData,
          customersData,
          uniqueCustomersData
        ] = await Promise.all([
          fetchTotalProducts(STORE_ID, params),
          fetchTotalSales(STORE_ID, params),
          fetchTotalRevenue(STORE_ID, params),
          fetchTotalCustomers(STORE_ID, params),
          fetchUniqueCustomers(STORE_ID, params)
        ]);

        setTotalProducts(productsData.total_products || 0);
        setTotalSales(salesData.total_sales || 0);
        setTotalRevenue(revenueData.total_revenue || 0);
        setTotalCustomers(customersData.total_customers || 0);
        setUniqueCustomers(uniqueCustomersData.unique_customers || 0);

        if (salesData.total_sales > 0 && revenueData.total_revenue > 0) {
          const avg = revenueData.total_revenue / salesData.total_sales;
          setAverageValue(avg);
        }

      } catch (err) {
        console.error('Error fetching KPIs:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchAllKPIs();
  }, [filterStatus, dateFrom, dateTo]);

  // Fetch Monthly Revenue
  useEffect(() => {
    const fetchRevenue = async () => {
      try {
        setRevenueLoading(true);
        console.log('Fetching monthly revenue for store:', STORE_ID);
        const data = await fetchMonthlyRevenue(STORE_ID);
        console.log('Monthly Revenue Response:', data);
        setMonthlyRevenue(data.monthly_revenue || []);
      } catch (err) {
        console.error('Error fetching monthly revenue:', err);
      } finally {
        setRevenueLoading(false);
      }
    };

    fetchRevenue();
  }, []);

  // Fetch Top Selling Categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setCategoriesLoading(true);
        console.log('Fetching top categories for store:', STORE_ID);
        const period = parseInt(filterPeriod);
        const data = await fetchTopSellingCategories(STORE_ID, period);
        console.log('Top Categories Response:', data);
        
        let categories = data.top_selling_categories || [];
        
        // Apply category filter
        if (filterCategory !== 'all') {
          categories = categories.filter(cat => 
            cat.category_name.toLowerCase() === filterCategory.toLowerCase()
          );
        }
        
        setTopCategories(categories);
      } catch (err) {
        console.error('Error fetching categories:', err);
      } finally {
        setCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, [filterPeriod, filterCategory]);

  // Fetch Recent Orders
  // Fetch Recent Orders
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setOrdersLoading(true);
        console.log('Fetching recent orders for store:', STORE_ID);
        
        // Build query parameters based on filters
        const queryParams = {
          page: currentPage,
          limit: ordersPerPage
        };
        
        // Add status filter if not "all"
        if (filterStatus !== 'all') {
          queryParams.status = filterStatus;
        }
        
        // Add search parameter to API call
        if (searchText.trim()) {
          queryParams.search = searchText.trim();
        }
        
        const data = await fetchRecentOrders(STORE_ID, queryParams);
        console.log('Recent Orders Response:', data);
        
        // Use orders directly from API (no frontend filtering needed)
        setRecentOrders(data.orders || []);
        setOrdersPagination(data.pagination || null);
      } catch (err) {
        console.error('Error fetching recent orders:', err);
      } finally {
        setOrdersLoading(false);
      }
    };

    fetchOrders();
  }, [filterStatus, searchText, currentPage, ordersPerPage]);

  // Fetch Top Dish Searches
  useEffect(() => {
    const fetchDishQueries = async () => {
      try {
        setDishQueriesLoading(true);
        console.log('Fetching top dish searches for store:', STORE_ID);
        const data = await fetchTopDishSearches(STORE_ID);
        console.log('Top Dish Searches Response:', data);
        setDishQueryData(data.data || []);
      } catch (err) {
        console.error('Error fetching dish queries:', err);
      } finally {
        setDishQueriesLoading(false);
      }
    };

    fetchDishQueries();
  }, []);

  const toggleSubstitutions = (productId) => {
    setExpandedProducts(prev => ({
      ...prev,
      [productId]: !prev[productId]
    }));
  };

  const generateQuickInsights = async () => {
    try {
      setSubstitutionsLoading(true);
      console.log('Generating quick insights for store:', STORE_ID);
      const data = await fetchProductSubstitutions(STORE_ID, 5);
      console.log('Quick Insights API Response:', data);
      console.log('Results array:', data.results);
      setProductSubstitutions(data.results || []);
    } catch (err) {
      console.error('Error generating quick insights:', err);
      console.error('Error details:', err.message);
    } finally {
      setSubstitutionsLoading(false);
    }
  };

  const generateAIInsights = async () => {
    try {
      setAiLoading(true);
      setAiError(null);
      console.log('Generating AI insights for store:', STORE_ID);
      const data = await fetchTopStockAlerts(STORE_ID);
      console.log('AI Insights Response:', data);
      setAiRecommendations(data.Ai_recommendations || []);
    } catch (err) {
      console.error('Error generating AI insights:', err);
      setAiError('Failed to generate insights. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  // Prepare chart data
  const getChartData = () => {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const chartData = monthNames.map((name, idx) => ({
      month: name,
      revenue: 0,
      index: idx + 1
    }));

    monthlyRevenue.forEach(item => {
      const monthIndex = item.month - 1;
      if (monthIndex >= 0 && monthIndex < 12) {
        chartData[monthIndex].revenue = item.total_revenue;
      }
    });

    return chartData;
  };
  // NEW: Handle "Show More" button
  const handleShowMore = () => {
    setOrdersPerPage(10);
    setCurrentPage(1); // Reset to first page when expanding
  };

  // NEW: Handle page navigation
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: document.getElementById('recent-orders-section')?.offsetTop - 100, behavior: 'smooth' });
  };

  // NEW: Calculate total pages
  const totalPages = ordersPagination ? Math.ceil(ordersPagination.total_items / ordersPerPage) : 1;
  
  const chartData = getChartData();
  const maxRevenue = Math.max(...chartData.map(d => d.revenue), 1);

  const categoryColors = [
    '#6366F1', '#3B82F6', '#8B5CF6', '#F59E0B', 
    '#10B981', '#EC4899', '#EF4444', '#14B8A6'
  ];

  const getDonutSegments = () => {
    if (topCategories.length === 0) return [];
    
    let currentAngle = -90;
    return topCategories.map((cat, idx) => {
      const percentage = cat.percentage || 0;
      const angle = (percentage / 100) * 360;
      const segment = {
        category: cat.category_name,
        percentage: percentage,
        color: categoryColors[idx % categoryColors.length],
        startAngle: currentAngle,
        endAngle: currentAngle + angle,
        sales: cat.total_sales,
        units: cat.units_sold
      };
      currentAngle += angle;
      return segment;
    });
  };

  const donutSegments = getDonutSegments();
  const topDishSearches = aggregateDishSearches(dishQueryData);
  const ingredientDemand = aggregateIngredientDemand(dishQueryData);
  const maxIngredientQueries = ingredientDemand.length > 0 ? ingredientDemand[0].queries : 1;

  // Get unique categories for filter dropdown
  const uniqueCategories = [...new Set(topCategories.map(cat => cat.category_name))];

  const handleApplyFilters = () => {
    // Filters are applied automatically through useEffect dependencies
    console.log('Filters applied:', { filterPeriod, filterCategory, filterStatus, searchText, dateFrom, dateTo });
    setShowDatePicker(false);
  };

  const handleClearDates = () => {
    setDateFrom('');
    setDateTo('');
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '₹0';
    if (value >= 100000) {
      return `₹${(value / 100000).toFixed(2)}L`;
    } else if (value >= 1000) {
      return `₹${(value / 1000).toFixed(1)}K`;
    }
    return `₹${value.toFixed(0)}`;
  };

  const formatNumber = (value) => {
    if (value === null || value === undefined) return '0';
    return value.toLocaleString();
  };

  const formatDateTime = (dateTimeStr) => {
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

  const getStatusColor = (status) => {
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

  const formatStatus = (status) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
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

  const getDemandLevel = (productCount) => {
    if (!productCount || productCount === 0) return 'Low';
    if (productCount >= 30) return 'High';
    if (productCount >= 15) return 'Medium';
    return 'Low';
  };

  return (
    <div className="flex h-screen bg-gray-50" style={{ fontFamily: "'Proxima Nova', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>
      <aside className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 space-y-8">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-50">
          <span className="text-indigo-600 font-bold text-lg">B2</span>
        </div>
        <nav className="flex flex-col items-center space-y-6">
          <button className="p-3 rounded-lg bg-indigo-50 text-indigo-600">
            <BarChart3 className="w-5 h-5" />
          </button>
          <button className="p-3 rounded-lg text-gray-400 hover:bg-gray-50">
            <Package className="w-5 h-5" />
          </button>
          <button className="p-3 rounded-lg text-gray-400 hover:bg-gray-50">
            <ShoppingCart className="w-5 h-5" />
          </button>
          <button className="p-3 rounded-lg text-gray-400 hover:bg-gray-50">
            <Users className="w-5 h-5" />
          </button>
          <button className="p-3 rounded-lg text-gray-400 hover:bg-gray-50">
            <TrendingUp className="w-5 h-5" />
          </button>
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-xl font-bold text-indigo-600">Buy2Cash</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-green-50 px-3 py-1.5 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-green-700">Online</span>
            </div>
            <Bell className="w-5 h-5 text-gray-400" />
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">HR Store</span>
              <ChevronDown className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">AI Analytics Dashboard</h1>
            <p className="text-sm text-gray-500">Integrate insights and predictive insights for your business</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="flex items-center space-x-3 mb-6">
            <div className="relative">
              <button 
                onClick={() => setShowDatePicker(!showDatePicker)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white text-black flex items-center space-x-2 hover:bg-gray-50"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{dateFrom && dateTo ? `${dateFrom.split('T')[0]} to ${dateTo.split('T')[0]}` : 'Select Date Range'}</span>
              </button>
              
              {showDatePicker && (
                <div className="absolute top-full left-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-10 w-96">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-sm text-gray-900">Select Date Range</h3>
                    {(dateFrom || dateTo) && (
                      <button 
                        onClick={handleClearDates}
                        className="text-xs text-indigo-600 hover:text-indigo-700"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">From Date</label>
                      <input 
                        type="datetime-local"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white text-black"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">To Date</label>
                      <input 
                        type="datetime-local"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white text-black"
                      />
                    </div>
                    {/* <button 
                      onClick={() => setShowDatePicker(false)}
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded text-sm font-medium hover:bg-indigo-700"
                    >
                      Apply Date Filter
                    </button> */}
                  </div>
                </div>
              )}
            </div>
            

            {/* <select 
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white text-black"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              {uniqueCategories.map((cat, idx) => (
                <option key={idx} value={cat}>{cat}</option>
              ))}
            </select> */}
            <select 
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white text-black"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="COMPLETED">Completed</option>
              <option value="PENDING">Pending</option>
              <option value="ACCEPTED">Accepted</option>
              <option value="IN_DELIVERY">In Delivery</option>
              <option value="PICKED_UP">Picked Up</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="EXPIRED">Expired</option>
            </select>
            <input 
              type="text" 
              placeholder="Search by Order ID, Customer Name or Phone..." 
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm flex-1 bg-white text-black placeholder-gray-400"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            {/* <button 
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
              onClick={handleApplyFilters}
            >
              Apply Filters
            </button> */}
          </div>

          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4 text-black">Business Performance</h2>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg border border-gray-200 ">
                <div className="text-xs text-gray-500 mb-1">TOTAL PRODUCTS</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatNumber(totalProducts)}</div>
                )}
                <div className="text-xs text-gray-400">Active inventory</div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">TOTAL SALES</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatNumber(totalSales)}</div>
                )}
                <div className="text-xs text-gray-400">Completed orders</div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">REVENUE</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatCurrency(totalRevenue)}</div>
                )}
                <div className="text-xs text-gray-400">Total earnings</div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">AVERAGE VALUE</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatCurrency(averageValue)}</div>
                )}
                <div className="text-xs text-gray-400">Per order</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-indigo-600 mr-2" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Quick Insights</h3>
                    <p className="text-xs text-gray-500">Products that may need attention</p>
                  </div>
                </div>
                <button 
                  onClick={generateQuickInsights}
                  disabled={substitutionsLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {substitutionsLoading ? 'Generating...' : 'Generate Insights'}
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto max-h-96">
                {substitutionsLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-4 bg-gray-50 rounded-lg animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : productSubstitutions.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-gray-500 mb-2">Click "Generate Insights" to find products that may need attention</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="text-xs text-gray-500 mb-2">
                      Found {productSubstitutions.length} products
                    </div>
                    {productSubstitutions.map((item) => {
                      const isExpanded = expandedProducts[item.product_id];
                      const substitutes = item.substitutes?.substitutes || [];
                      
                      return (
                        <div key={item.product_id} className="border border-gray-200 rounded-lg overflow-hidden">
                          <div className="p-4 bg-white">
                            <div className="font-medium text-sm text-gray-900 mb-1">
                              {item.substitutes?.original_product?.name || 'Unknown Product'}
                            </div>
                            <div className="text-xs text-gray-600 mb-2">
                              Consider offering a discount to boost sales.
                            </div>
                            <button
                              onClick={() => toggleSubstitutions(item.product_id)}
                              className="px-4 py-1.5 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 transition-colors"
                            >
                              {isExpanded ? 'Hide Substitutions' : 'Show Substitutions'}
                            </button>
                          </div>
                          
                          {isExpanded && substitutes.length > 0 && (
                            <div className="px-4 pb-4 bg-gray-50">
                              <div className="text-xs font-medium text-gray-700 mb-2">Substitution Suggestions:</div>
                              <div className="space-y-1">
                                {substitutes.map((sub, idx) => (
                                  <div key={idx} className="text-xs text-gray-600 pl-3">
                                    • <span className="font-medium">{sub.product_name}</span>
                                    {' '}({sub.reason})
                                    {sub.price_difference !== 0 && (
                                      <span className={sub.price_difference > 0 ? 'text-red-600' : 'text-green-600'}>
                                        {' '}₹{Math.abs(sub.price_difference)} {sub.price_difference > 0 ? 'more' : 'less'}
                                      </span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-200 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-gray-900">AI-Powered Analysis</h3>
                  <p className="text-xs text-gray-500">Advanced insights from machine learning</p>
                </div>
                <button 
                  onClick={generateAIInsights}
                  disabled={aiLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {aiLoading ? 'Generating...' : 'Generate Insights'}
                </button>
              </div>

              {aiError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{aiError}</p>
                </div>
              )}

              <div className="flex-1 overflow-y-auto max-h-96">
                {aiLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-4 bg-gray-50 rounded-lg animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                      </div>
                    ))}
                  </div>
                ) : aiRecommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-gray-500">
                      Click "Generate Insights" to get AI-powered recommendations for boosting sales and optimizing inventory.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {aiRecommendations.map((rec, idx) => (
                      <div key={idx} className="p-4 bg-white border border-gray-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <div className="font-medium text-sm text-gray-900">
                            {idx + 1}. {rec.ProductName}
                          </div>
                          <div className="text-xs text-gray-500">
                            MRP: ₹{rec.mrpPrice} | Offer: ₹{rec.offerPrice}
                          </div>
                        </div>
                        <div className="mb-2">
                          <span className="text-xs font-semibold text-indigo-600">Recommendation: </span>
                          <span className="text-xs text-gray-700">{rec.recommendation}</span>
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-gray-600">Reasoning: </span>
                          <span className="text-xs text-gray-600">{rec.reasoning}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4 text-black">Performance Analytics</h2>
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h3 className="font-semibold mb-4 text-black">Monthly Revenue Trend</h3>
                {revenueLoading ? (
                  <div className="h-64 flex items-center justify-center">
                    <div className="animate-pulse text-gray-400">Loading chart data...</div>
                  </div>
                ) : (
                  <div className="relative">
                    <div className="h-64 relative" style={{ background: 'linear-gradient(180deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.02) 100%)' }}>
                      <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-500 pr-2">
                        <span>₹{Math.round(maxRevenue)}</span>
                        <span>₹{Math.round(maxRevenue * 0.75)}</span>
                        <span>₹{Math.round(maxRevenue * 0.5)}</span>
                        <span>₹{Math.round(maxRevenue * 0.25)}</span>
                        <span>₹0</span>
                      </div>
                      
                      <svg className="w-full h-full pl-12" viewBox="0 0 800 300" preserveAspectRatio="none">
                        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
                          <line
                            key={i}
                            x1="0"
                            y1={256 * (1 - pct) + 22}
                            x2="800"
                            y2={256 * (1 - pct) + 22}
                            stroke="#E5E7EB"
                            strokeWidth="1"
                          />
                        ))}
                        
                        <defs>
                          <linearGradient id="areaGradient" x1="0" x2="0" y1="0" y2="1">
                            <stop offset="0%" stopColor="#6366F1" stopOpacity="0.2"/>
                            <stop offset="100%" stopColor="#6366F1" stopOpacity="0.02"/>
                          </linearGradient>
                        </defs>
                        
                        <path
                          d={`M 0 ${278} ${chartData.map((d, i) => {
                            const x = (i / 11) * 800;
                            const y = 278 - ((d.revenue / maxRevenue) * 240);
                            return `L ${x} ${y}`;
                          }).join(' ')} L 800 ${278} Z`}
                          fill="url(#areaGradient)"
                        />
                        
                        <path
                          d={chartData.map((d, i) => {
                            const x = (i / 11) * 800;
                            const y = 278 - ((d.revenue / maxRevenue) * 240);
                            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                          }).join(' ')}
                          fill="none"
                          stroke="#6366F1"
                          strokeWidth="2"
                        />
                        
                        {chartData.map((d, i) => {
                          const x = (i / 11) * 800;
                          const y = 278 - ((d.revenue / maxRevenue) * 240);
                          const tooltipY = Math.max(y - 35, 10);
                          
                          return (
                            <g key={i}>
                              <circle
                                cx={x}
                                cy={y}
                                r="20"
                                fill="transparent"
                                onMouseEnter={() => setHoveredPoint(i)}
                                onMouseLeave={() => setHoveredPoint(null)}
                                style={{ cursor: 'pointer' }}
                              />
                              <circle
                                cx={x}
                                cy={y}
                                r="4"
                                fill="#6366F1"
                                stroke="white"
                                strokeWidth="2"
                                style={{ pointerEvents: 'none' }}
                              />
                              {hoveredPoint === i && (
                                <g style={{ pointerEvents: 'none' }}>
                                  <rect
                                    x={x - 40}
                                    y={tooltipY}
                                    width="80"
                                    height="30"
                                    fill="white"
                                    stroke="#6366F1"
                                    strokeWidth="1.5"
                                    rx="4"
                                    filter="url(#shadow)"
                                  />
                                  <text
                                    x={x}
                                    y={tooltipY + 14}
                                    textAnchor="middle"
                                    fontSize="11"
                                    fill="#6366F1"
                                    fontWeight="600"
                                  >
                                    {d.month}
                                  </text>
                                  <text
                                    x={x}
                                    y={tooltipY + 26}
                                    textAnchor="middle"
                                    fontSize="10"
                                    fill="#374151"
                                  >
                                    {formatCurrency(d.revenue)}
                                  </text>
                                </g>
                              )}
                            </g>
                          );
                        })}
                        
                        <defs>
                          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                            <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.15"/>
                          </filter>
                        </defs>
                      </svg>
                    </div>
                    
                    <div className="flex justify-between text-xs text-gray-500 mt-2 pl-12">
                      {chartData.map((d, i) => (
                        <span key={i}>{d.month}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h3 className="font-semibold mb-4 text-black">Product Category Distribution</h3>
                {categoriesLoading ? (
                  <div className="h-64 flex items-center justify-center">
                    <div className="animate-pulse text-gray-400">Loading categories...</div>
                  </div>
                ) : topCategories.length === 0 ? (
                  <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
                    No category data available
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-center h-64 relative">
                      <div className="relative w-48 h-48">
                        <svg 
                          viewBox="0 0 100 100" 
                          className="transform -rotate-90"
                          onMouseMove={(e) => {
                            const rect = e.currentTarget.getBoundingClientRect();
                            setTooltipPos({
                              x: e.clientX - rect.left,
                              y: e.clientY - rect.top
                            });
                          }}
                        >
                          <circle cx="50" cy="50" r="40" fill="none" stroke="#F3F4F6" strokeWidth="20"/>
                          
                          {donutSegments.map((segment, idx) => {
                            const startAngle = (segment.startAngle * Math.PI) / 180;
                            const endAngle = (segment.endAngle * Math.PI) / 180;
                            const largeArc = segment.percentage > 50 ? 1 : 0;
                            
                            const x1 = 50 + 40 * Math.cos(startAngle);
                            const y1 = 50 + 40 * Math.sin(startAngle);
                            const x2 = 50 + 40 * Math.cos(endAngle);
                            const y2 = 50 + 40 * Math.sin(endAngle);
                            
                            const pathData = [
                              `M 50 50`,
                              `L ${x1} ${y1}`,
                              `A 40 40 0 ${largeArc} 1 ${x2} ${y2}`,
                              `Z`
                            ].join(' ');
                            
                            return (
                              <path
                                key={idx}
                                d={pathData}
                                fill={segment.color}
                                opacity={hoveredSegment === idx ? "1" : "0.9"}
                                style={{ cursor: 'pointer', transition: 'opacity 0.2s' }}
                                onMouseEnter={() => setHoveredSegment(idx)}
                                onMouseLeave={() => setHoveredSegment(null)}
                              />
                            );
                          })}
                          
                          <circle cx="50" cy="50" r="25" fill="white"/>
                        </svg>
                      </div>
                      
                      {hoveredSegment !== null && (
                        <div 
                          className="absolute bg-white rounded-lg shadow-xl border-2 border-indigo-500 p-3 pointer-events-none z-20"
                          style={{
                            left: `${tooltipPos.x + 15}px`,
                            top: `${tooltipPos.y - 60}px`,
                            minWidth: '180px',
                            transition: 'left 0.1s ease-out, top 0.1s ease-out'
                          }}
                        >
                          <div className="text-left">
                            <div className="text-sm font-semibold text-gray-900 mb-1">
                              {donutSegments[hoveredSegment].category}
                            </div>
                            <div className="text-sm text-indigo-600 font-medium mb-1">
                              {donutSegments[hoveredSegment].percentage.toFixed(1)}% of sales
                            </div>
                            <div className="text-xs text-gray-500">
                              ₹{donutSegments[hoveredSegment].sales.toLocaleString()}
                            </div>
                            <div className="text-xs text-gray-500">
                              {donutSegments[hoveredSegment].units} units
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-4 justify-center mt-4">
                      {donutSegments.map((segment, idx) => (
                        <div 
                          key={idx} 
                          className="flex items-center space-x-2"
                        >
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: segment.color }}
                          ></div>
                          <span className="text-xs text-gray-600">
                            {segment.category} ({segment.percentage.toFixed(1)}%)
                          </span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4 text-black">Customer Management</h2>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">TOTAL CUSTOMERS</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatNumber(totalCustomers)}</div>
                )}
                <div className="text-xs text-gray-400">All orders</div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">UNIQUE CUSTOMERS</div>
                {loading ? (
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                ) : (
                  <div className="text-2xl font-bold text-gray-900 mb-1">{formatNumber(uniqueCustomers)}</div>
                )}
                <div className="text-xs text-gray-400">Individual buyers</div>
              </div>
            </div>

            <div id="recent-orders-section" className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="font-semibold text-black">Recent Orders - Detailed View</h3>
                {ordersPagination && (
                  <p className="text-xs text-gray-500 mt-1">
                    Showing {((currentPage - 1) * ordersPerPage) + 1} - {Math.min(currentPage * ordersPerPage, ordersPagination.total_items)} of {ordersPagination.total_items} orders
                  </p>
                )}
              </div>
              {ordersLoading ? (
                <div className="p-8 text-center">
                  <div className="animate-pulse text-gray-400">Loading orders...</div>
                </div>
              ) : recentOrders.length === 0 ? (
                <div className="p-8 text-center text-gray-400 text-sm">
                  No orders found
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date & Time</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {recentOrders.map((order) => (
                          <tr key={order.order_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm text-gray-900">{order.order_id}</td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">{order.customer.name}</div>
                              <div className="text-xs text-gray-500">{order.customer.phone}</div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {formatDateTime(order.date_time.created)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">{order.items_count}</td>
                            <td className="px-6 py-4 text-sm text-gray-900">₹{order.amount.total}</td>
                            <td className="px-6 py-4 text-sm">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(order.status)}`}>
                                {formatStatus(order.status)}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {order.payment_method === 'ONLINE' ? 'Online' : 'COD'}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {order.category === 'CUSTOMER_APP' ? 'Customer App' : order.category}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  
                  {/* NEW: Show More Button and Pagination Controls */}
                  <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
                    {ordersPerPage === 5 && ordersPagination && ordersPagination.total_items > 5 && (
                      <div className="flex justify-center mb-4">
                        <button
                          onClick={handleShowMore}
                          className="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                        >
                          Show More
                        </button>
                      </div>
                    )}
                    
                    {ordersPerPage === 10 && totalPages > 1 && (
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600">
                          Page {currentPage} of {totalPages}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            <ChevronLeft className="w-4 h-4 text-gray-600" />
                          </button>
                          
                          {[...Array(totalPages)].map((_, idx) => {
                            const pageNum = idx + 1;
                            // Show first page, last page, current page, and pages around current
                            if (
                              pageNum === 1 ||
                              pageNum === totalPages ||
                              (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                            ) {
                              return (
                                <button
                                  key={pageNum}
                                  onClick={() => handlePageChange(pageNum)}
                                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                                    currentPage === pageNum
                                      ? 'bg-indigo-600 text-white'
                                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-100'
                                  }`}
                                >
                                  {pageNum}
                                </button>
                              );
                            } else if (
                              pageNum === currentPage - 2 ||
                              pageNum === currentPage + 2
                            ) {
                              return <span key={pageNum} className="text-gray-400">...</span>;
                            }
                            return null;
                          })}
                          
                          <button
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            <ChevronRight className="w-4 h-4 text-gray-600" />
                          </button>
                        </div>
                        
                        <div className="text-sm text-gray-600">
                          {ordersPagination.total_items} total orders
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold mb-4 text-black ">Top Dish Searches</h3>
              {dishQueriesLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-10 bg-gray-200 rounded text-black"></div>
                    </div>
                  ))}
                </div>
              ) : topDishSearches.length === 0 ? (
                <div className="text-center py-8 text-black text-sm">
                  No dish search data available
                </div>
              ) : (
                <div className="space-y-3">
                  {topDishSearches.map((dish, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-sm font-semibold text-indigo-600 ">
                          {idx + 1}
                        </div>
                        <div>
                          <div className="font-medium text-sm text-black">{dish.name}</div>
                          <div className="text-xs text-gray-500">Popular dish</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="font-semibold text-sm text-black">{dish.searches.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold mb-4 text-black">Ingredient Demand (from Dish Queries)</h3>
              {dishQueriesLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-8 bg-gray-200 rounded mb-2"></div>
                      <div className="h-2 bg-gray-200 rounded"></div>
                    </div>
                  ))}
                </div>
              ) : ingredientDemand.length === 0 ? (
                <div className="text-center py-8 text-gray-400 text-sm">
                  No ingredient demand data available
                </div>
              ) : (
                <div className="space-y-3">
                  {ingredientDemand.map((ingredient, idx) => (
                    <div key={idx}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-700">{ingredient.name}</span>
                        <span className="text-sm font-medium text-indigo-600">{ingredient.queries} queries</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${(ingredient.queries / maxIngredientQueries) * 100}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="font-semibold text-black">Detailed Dish Query Analytics</h3>
              <p className="text-xs text-gray-500 mt-1">
                Customer search queries with product recommendations
              </p>
            </div>
            {dishQueriesLoading ? (
              <div className="p-8 text-center">
                <div className="animate-pulse text-gray-400">Loading dish queries...</div>
              </div>
            ) : dishQueryData.length === 0 ? (
              <div className="p-8 text-center text-gray-400 text-sm">
                No dish queries found
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Query</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dish Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cuisine</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dietary</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Meal Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Products Found</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Demand Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Searched</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dishQueryData.map((item, idx) => {
                      const productCount = Array.isArray(item.product_name) ? item.product_name.length : 0;
                      const demandLevel = getDemandLevel(productCount);
                      
                      return (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm text-gray-900">{item.query}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {item.dishbased && item.dishbased.length > 0 ? item.dishbased.join(', ') : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {item.cuisinebased && item.cuisinebased.length > 0 ? item.cuisinebased.join(', ') : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {item.dietarybased && item.dietarybased.length > 0 ? item.dietarybased.join(', ') : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {item.timebased && item.timebased.length > 0 ? item.timebased.join(', ') : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{productCount}</td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              demandLevel === 'High' ? 'bg-green-100 text-green-700' :
                              demandLevel === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {demandLevel}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">{formatTimestamp(item.timestamp)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}