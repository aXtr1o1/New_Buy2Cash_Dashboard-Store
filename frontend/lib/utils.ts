// Utility functions for formatting and data processing

export const formatCurrency = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '₹0';
  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)}L`;
  } else if (value >= 1000) {
    return `₹${(value / 1000).toFixed(1)}K`;
  }
  return `₹${value.toFixed(0)}`;
};

export const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '0';
  return value.toLocaleString();
};

export const formatDateTime = (dateTimeStr: string | null | undefined): string => {
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

export const formatTimestamp = (timestamp: string | null | undefined): string => {
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

export const formatStatus = (status: string): string => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const getStatusColor = (status: string): string => {
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

export const getDemandLevel = (productCount: number): string => {
  if (!productCount || productCount === 0) return 'Low';
  if (productCount >= 30) return 'High';
  if (productCount >= 15) return 'Medium';
  return 'Low';
};

export const aggregateDishSearches = (dishQueryData: any[]): Array<{ name: string; searches: number }> => {
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

export const aggregateIngredientDemand = (dishQueryData: any[]): Array<{ name: string; queries: number }> => {
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

