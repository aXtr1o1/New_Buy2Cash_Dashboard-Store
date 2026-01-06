// useDashboardData.ts - Custom Hook for Dashboard Data Management

import { useState, useEffect } from 'react';
import {
  STORE_ID,
  fetchTotalProducts,
  fetchTotalSales,
  fetchTotalRevenue,
  fetchAvgOrderValue,
  fetchTotalCustomers,
  fetchUniqueCustomers,
  fetchTopCustomers,
  fetchMonthlyRevenue,
  fetchProductsByCategory,
  fetchRecentOrders,
  fetchTopDishSearches,
  fetchTopSellingProducts,
  fetchTopStockAlerts,
  fetchQuickAnalysis
} from './api';

export const useDashboardData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // KPI States
  const [totalProducts, setTotalProducts] = useState<number | null>(null);
  const [totalSales, setTotalSales] = useState<number | null>(null);
  const [totalRevenue, setTotalRevenue] = useState<number | null>(null);
  const [averageValue, setAverageValue] = useState<number | null>(null);
  const [totalCustomers, setTotalCustomers] = useState<number | null>(null);
  const [uniqueCustomers, setUniqueCustomers] = useState<number | null>(null);
  const [topCustomers, setTopCustomers] = useState<number | null>(null);
  
  // AI-Powered Analysis State
  const [aiRecommendations, setAiRecommendations] = useState<any[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  
  // Top Selling Products State
  const [topProducts, setTopProducts] = useState<any[]>([]);
  const [topProductsLoading, setTopProductsLoading] = useState(false);
  
  // Quick Insights (Substitution Insights) State
  const [substitutionInsights, setSubstitutionInsights] = useState<any[]>([]);
  const [substitutionLoading, setSubstitutionLoading] = useState(false);
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());
  
  // Top 10 Products State
  const [top10Products, setTop10Products] = useState<any[]>([]);
  const [top10Loading, setTop10Loading] = useState(true);
  
  // Time Period Sales State
  const [timePeriodSales, setTimePeriodSales] = useState({
    morning: 0,
    afternoon: 0,
    evening: 0,
    night: 0
  });
  const [timePeriodLoading, setTimePeriodLoading] = useState(true);
  
  // Monthly Revenue State
  const [monthlyRevenue, setMonthlyRevenue] = useState<any[]>([]);
  const [revenueLoading, setRevenueLoading] = useState(true);
  
  // Category Distribution State
  const [categoryDistribution, setCategoryDistribution] = useState<any[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);

  // Recent Orders State
  const [recentOrders, setRecentOrders] = useState<any[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(true);
  const [ordersPagination, setOrdersPagination] = useState<any>(null);
  const [ordersPerPage, setOrdersPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);  

  // Dish Query Data State
  const [dishQueryData, setDishQueryData] = useState<any[]>([]);
  const [dishQueriesLoading, setDishQueriesLoading] = useState(true);

  // Filter States (applied filters)
  const [filterStatus, setFilterStatus] = useState('');
  const [searchText, setSearchText] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  
  // Pending Filter States (temporary, not yet applied)
  const [pendingFilterStatus, setPendingFilterStatus] = useState('');
  const [pendingSearchText, setPendingSearchText] = useState('');
  const [pendingDateFrom, setPendingDateFrom] = useState('');
  const [pendingDateTo, setPendingDateTo] = useState('');

  // Build filter params
  const getFilterParams = () => {
    const params: any = {};
    if (filterStatus) params.status = filterStatus;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    return params;
  };

  // Fetch all KPI data
  useEffect(() => {
    const fetchAllKPIs = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = getFilterParams();

        const [
          productsData,
          salesData,
          revenueData,
          avgOrderData,
          customersData,
          uniqueCustomersData,
          topCustomersData
        ] = await Promise.all([
          fetchTotalProducts(STORE_ID, params),
          fetchTotalSales(STORE_ID, params),
          fetchTotalRevenue(STORE_ID, params),
          fetchAvgOrderValue(STORE_ID, params),
          fetchTotalCustomers(STORE_ID, params),
          fetchUniqueCustomers(STORE_ID, params),
          fetchTopCustomers(STORE_ID, params)
        ]);

        setTotalProducts(productsData.products_count || 0);
        setTotalSales(salesData.sales_count || 0);
        setTotalRevenue(revenueData.total_revenue || 0);
        setAverageValue(avgOrderData.avg_order_value || 0);
        setTotalCustomers(customersData.total_customers || 0);
        setUniqueCustomers(uniqueCustomersData.unique_customers || 0);
        setTopCustomers(topCustomersData.top_customer?.total_spent || 0);

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
        const params = getFilterParams();
        const data = await fetchMonthlyRevenue(STORE_ID, params);
        setMonthlyRevenue(data.monthly_revenue || []);
      } catch (err) {
        console.error('Error fetching monthly revenue:', err);
      } finally {
        setRevenueLoading(false);
      }
    };

    fetchRevenue();
  }, [filterStatus, dateFrom, dateTo]);

  // Fetch Category Distribution
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setCategoriesLoading(true);
        const params = getFilterParams();
        const data = await fetchProductsByCategory(STORE_ID, params);
        setCategoryDistribution(data.categories_distribution || []);
      } catch (err) {
        console.error('Error fetching categories:', err);
      } finally {
        setCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, [filterStatus, dateFrom, dateTo]);

  // Fetch Recent Orders
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setOrdersLoading(true);
        
        const queryParams: any = {
          page: currentPage,
          limit: ordersPerPage
        };
        
        if (filterStatus) queryParams.status = filterStatus;
        if (searchText.trim()) queryParams.search = searchText.trim();
        if (dateFrom) queryParams.date_from = dateFrom;
        if (dateTo) queryParams.date_to = dateTo;
        
        const data = await fetchRecentOrders(STORE_ID, queryParams);
        setRecentOrders(data.orders || []);
        setOrdersPagination(data.pagination || null);
      } catch (err) {
        console.error('Error fetching recent orders:', err);
      } finally {
        setOrdersLoading(false);
      }
    };

    fetchOrders();
  }, [filterStatus, searchText, currentPage, ordersPerPage, dateFrom, dateTo]);

  // Fetch Top Dish Searches
  useEffect(() => {
    const fetchDishQueries = async () => {
      try {
        setDishQueriesLoading(true);
        const data = await fetchTopDishSearches(STORE_ID);
        setDishQueryData(data.data || []);
      } catch (err) {
        console.error('Error fetching dish queries:', err);
      } finally {
        setDishQueriesLoading(false);
      }
    };

    fetchDishQueries();
  }, []);

  // Fetch Top 10 Products
  useEffect(() => {
    const fetchTop10 = async () => {
      try {
        setTop10Loading(true);
        const params = { ...getFilterParams(), limit: 10 };
        const data = await fetchTopSellingProducts(STORE_ID, params);
        setTop10Products(data.top_selling_products || []);
      } catch (err) {
        console.error('Error fetching top 10 products:', err);
      } finally {
        setTop10Loading(false);
      }
    };

    fetchTop10();
  }, [filterStatus, dateFrom, dateTo]);

  // Fetch Time Period Sales
  useEffect(() => {
    const fetchTimePeriodSales = async () => {
      try {
        setTimePeriodLoading(true);
        const params = getFilterParams();
        const data = await fetchRecentOrders(STORE_ID, { ...params, limit: 1000 });
        
        const orders = data.orders || [];
        const periods = {
          morning: 0,
          afternoon: 0,
          evening: 0,
          night: 0
        };

        orders.forEach((order: any) => {
          if (order.date_time?.created) {
            const date = new Date(order.date_time.created);
            const hour = date.getHours();
            
            if (hour >= 6 && hour < 12) {
              periods.morning += order.amount.total;
            } else if (hour >= 12 && hour < 18) {
              periods.afternoon += order.amount.total;
            } else if (hour >= 18 && hour < 21) {
              periods.evening += order.amount.total;
            } else {
              periods.night += order.amount.total;
            }
          }
        });

        setTimePeriodSales(periods);
      } catch (err) {
        console.error('Error fetching time period sales:', err);
      } finally {
        setTimePeriodLoading(false);
      }
    };

    fetchTimePeriodSales();
  }, [filterStatus, dateFrom, dateTo]);

  const generateTopProducts = async () => {
    try {
      setTopProductsLoading(true);
      const params = { ...getFilterParams(), limit: 5 };
      const data = await fetchTopSellingProducts(STORE_ID, params);
      setTopProducts(data.top_selling_products || []);
    } catch (err) {
      console.error('Error generating top products:', err);
    } finally {
      setTopProductsLoading(false);
    }
  };

  const generateSubstitutionInsights = async () => {
    try {
      setSubstitutionLoading(true);
      const data = await fetchQuickAnalysis(STORE_ID);
      setSubstitutionInsights(data.results || []);
      // Expand first insight by default
      if (data.results && data.results.length > 0) {
        setExpandedInsights(new Set([data.results[0].product_id]));
      }
    } catch (err) {
      console.error('Error generating substitution insights:', err);
    } finally {
      setSubstitutionLoading(false);
    }
  };

  const toggleInsightExpanded = (productId: string) => {
    setExpandedInsights(prev => {
      const newSet = new Set(prev);
      if (newSet.has(productId)) {
        newSet.delete(productId);
      } else {
        newSet.add(productId);
      }
      return newSet;
    });
  };

  const generateAIInsights = async () => {
    try {
      setAiLoading(true);
      setAiError(null);
      const data = await fetchTopStockAlerts(STORE_ID);
      setAiRecommendations(data.Ai_recommendations || []);
    } catch (err) {
      console.error('Error generating AI insights:', err);
      setAiError('Failed to generate insights. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleShowMore = () => {
    setOrdersPerPage(10);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleClearDates = () => {
    setPendingDateFrom('');
    setPendingDateTo('');
  };

  const applyFilters = () => {
    setFilterStatus(pendingFilterStatus);
    setSearchText(pendingSearchText);
    setDateFrom(pendingDateFrom);
    setDateTo(pendingDateTo);
    setCurrentPage(1); // Reset to first page when applying filters
  };

  return {
    // Loading states
    loading,
    error,
    revenueLoading,
    categoriesLoading,
    ordersLoading,
    dishQueriesLoading,
    top10Loading,
    timePeriodLoading,
    aiLoading,
    aiError,
    topProductsLoading,
    substitutionLoading,
    
    // KPI data
    totalProducts,
    totalSales,
    totalRevenue,
    averageValue,
    totalCustomers,
    uniqueCustomers,
    topCustomers,
    
    // Chart data
    monthlyRevenue,
    categoryDistribution,
    top10Products,
    timePeriodSales,
    
    // Orders data
    recentOrders,
    ordersPagination,
    ordersPerPage,
    currentPage,
    
    // Dish data
    dishQueryData,
    
    // AI data
    aiRecommendations,
    topProducts,
    
    // Substitution Insights
    substitutionInsights,
    expandedInsights,
    generateSubstitutionInsights,
    toggleInsightExpanded,
    
    // Filters (applied)
    filterStatus,
    searchText,
    dateFrom,
    dateTo,
    showDatePicker,
    setShowDatePicker,
    
    // Pending Filters
    pendingFilterStatus,
    setPendingFilterStatus,
    pendingSearchText,
    setPendingSearchText,
    pendingDateFrom,
    setPendingDateFrom,
    pendingDateTo,
    setPendingDateTo,
    
    // Actions
    generateTopProducts,
    generateAIInsights,
    generateSubstitutionInsights,
    toggleInsightExpanded,
    handleShowMore,
    handlePageChange,
    handleClearDates,
    applyFilters,
    getFilterParams
  };
};