import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv("config.env")

class Buy2CashException(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class DatabaseConnectionError(Buy2CashException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=503)

class StoreNotFoundError(Buy2CashException):
    def __init__(self, store_id: str):
        super().__init__(f"Store {store_id} not found", status_code=404)

class ValidationError(Buy2CashException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=422)

def convert_objectids_to_strings(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ObjectId to string for JSON response"""
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, dict):
                convert_objectids_to_strings(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectids_to_strings(item)
    return document

def validate_store_id(store_id: str) -> ObjectId:
    """Validate store ID"""
    try:
        return ObjectId(store_id)
    except:
        raise ValidationError(f"Invalid store ID: {store_id}")

def safe_divide(numerator: float, denominator: float) -> float:
    """Safe division"""
    return round(numerator / denominator, 2) if denominator > 0 else 0.0

def get_stores_data(sellers_collection, orders_collection, products_collection) -> Dict[str, Any]:
    """Get all active stores with enhanced stats"""
    try:
        stores = list(sellers_collection.find(
            {"status": "APPROVED", "isActive": True},
            {"_id": 1, "storeName": 1, "storeContactName": 1, "phoneNumber": 1, "address": 1, "payoutBalance": 1}
        ))
        
        formatted_stores = []
        for store in stores:
            convert_objectids_to_strings(store)
            store_id = ObjectId(store["_id"])

            total_products = products_collection.count_documents({"seller": store_id, "status": "APPROVED"})
            recent_orders = orders_collection.count_documents({
                "seller": store_id,
                "createdAt": {"$gte": datetime.now() - timedelta(days=30)}
            })
            
            formatted_stores.append({
                "store_id": store["_id"],
                "store_name": store.get("storeName", "Unknown Store"),
                "contact_name": store.get("storeContactName", ""),
                "phone": store.get("phoneNumber", ""),
                "address": store.get("address", ""),
                "payout_balance": round(float(store.get("payoutBalance", 0)), 2),
                "total_products": total_products,
                "recent_orders": recent_orders
            })
        
        return {"stores": formatted_stores}
        
    except Exception as e:
        logger.exception("Failed to fetch stores")
        raise DatabaseConnectionError(f"Failed to fetch stores: {str(e)}")

def get_top_products_data(orders_collection, products_collection, categories_collection, units_collection, store_id: str, limit: int = 10, period: int = 30) -> Dict[str, Any]:
    """Get top selling products with comprehensive data"""
    try:
        store_obj_id = validate_store_id(store_id)
        start_date = datetime.now() - timedelta(days=period)
        
        pipeline = [
            {"$match": {"seller": store_obj_id, "status": {"$nin": ["ABANDONED", "CANCELLED"]}, "createdAt": {"$gte": start_date}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items._id",
                "product_name": {"$first": "$items.productName"},
                "units_sold": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": "$items.subTotal"},
                "mrp_price": {"$first": "$items.mrpPrice"},
                "offer_price": {"$first": "$items.offerPrice"}
            }},
            {"$lookup": {"from": "products", "localField": "_id", "foreignField": "_id", "as": "product_info"}},
            {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "categories", "localField": "product_info.category", "foreignField": "_id", "as": "category_info"}},
            {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "units", "localField": "product_info.unit", "foreignField": "_id", "as": "unit_info"}},
            {"$unwind": {"path": "$unit_info", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"units_sold": -1}},
            {"$limit": limit}
        ]
        
        results = list(orders_collection.aggregate(pipeline))
        
        products = []
        for i, result in enumerate(results):
            convert_objectids_to_strings(result)
            
            mrp = float(result.get("mrp_price", 0))
            offer = float(result.get("offer_price", 0))
            discount = round(((mrp - offer) / mrp * 100), 2) if mrp > 0 else 0
            
            products.append({
                "rank": i + 1,
                "product_id": result.get("_id", ""),
                "product_name": result.get("product_name", "Unknown"),
                "category": result.get("category_info", {}).get("name", "Uncategorized"),
                "unit": result.get("unit_info", {}).get("name", "Unit"),
                "units_sold": result.get("units_sold", 0),
                "total_revenue": round(result.get("total_revenue", 0), 2),
                "mrp_price": round(mrp, 2),
                "offer_price": round(offer, 2),
                "discount_percentage": discount,
                "current_stock": result.get("product_info", {}).get("stockQuantity", 0)
            })
        
        return {"top_selling_products": products}
        
    except Exception as e:
        logger.exception(f"Failed to get top products for store {store_id}")
        raise DatabaseConnectionError(f"Failed to get top products: {str(e)}")
    


def get_low_selling_products_data(
    orders_collection,
    store_id: str,
    limit: int = 10,
    period: int = 30
) -> Dict[str, Any]:
    """Get lowest selling products with comprehensive data"""
    try:
        store_obj_id = validate_store_id(store_id)
        start_date = datetime.now() - timedelta(days=period)

        pipeline = [
            {
                "$match": {
                    "seller": store_obj_id,
                    "status": {"$nin": ["ABANDONED", "CANCELLED"]},
                    "createdAt": {"$gte": start_date}
                }
            },
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items._id",
                    "product_name": {"$first": "$items.productName"},
                    "units_sold": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": "$items.subTotal"},
                    "mrp_price": {"$first": "$items.mrpPrice"},
                    "offer_price": {"$first": "$items.offerPrice"}
                }
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }
            },
            {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "product_info.category",
                    "foreignField": "_id",
                    "as": "category_info"
                }
            },
            {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "units",
                    "localField": "product_info.unit",
                    "foreignField": "_id",
                    "as": "unit_info"
                }
            },
            {"$unwind": {"path": "$unit_info", "preserveNullAndEmptyArrays": True}},

            # Sorting ASCENDING (low selling first)
            {"$sort": {"units_sold": 1}},

            {"$limit": limit}
        ]

        results = list(orders_collection.aggregate(pipeline))

        products = []
        for i, result in enumerate(results):
            convert_objectids_to_strings(result)

            mrp = float(result.get("mrp_price", 0))
            offer = float(result.get("offer_price", 0))
            discount = round(((mrp - offer) / mrp * 100), 2) if mrp > 0 else 0

            products.append({
                "rank": i + 1,
                "product_id": result.get("_id", ""),
                "product_name": result.get("product_name", "Unknown"),
                "category": result.get("category_info", {}).get("name", "Uncategorized"),
                "unit": result.get("unit_info", {}).get("name", "Unit"),
                "units_sold": result.get("units_sold", 0),
                "total_revenue": round(result.get("total_revenue", 0), 2),
                "mrp_price": round(mrp, 2),
                "offer_price": round(offer, 2),
                "discount_percentage": discount,
                "current_stock": result.get("product_info", {}).get("stockQuantity", 0)
            })

        return {"low_selling_products": products}

    except Exception as e:
        logger.exception(f"Failed to get low selling products for store {store_id}")
        raise DatabaseConnectionError(f"Failed to get low selling products: {str(e)}")


def get_categories_data(orders_collection, categories_collection, subcategories_collection, store_id: str, period: int = 30) -> Dict[str, Any]:
    """Get top selling categories with subcategory info"""
    try:
        store_obj_id = validate_store_id(store_id)
        start_date = datetime.now() - timedelta(days=period)
        
        pipeline = [
            {"$match": {"seller": store_obj_id, "status": {"$nin": ["ABANDONED", "CANCELLED"]}, "createdAt": {"$gte": start_date}}},
            {"$unwind": "$items"},
            {"$lookup": {"from": "products", "localField": "items._id", "foreignField": "_id", "as": "product"}},
            {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "categories", "localField": "product.category", "foreignField": "_id", "as": "category"}},
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "subCategories", "localField": "product.subCategory", "foreignField": "_id", "as": "subcategory"}},
            {"$unwind": {"path": "$subcategory", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$category._id",
                "category_name": {"$first": "$category.name"},
                "total_sales": {"$sum": "$items.subTotal"},
                "units_sold": {"$sum": "$items.quantity"},
                "subcategories": {"$addToSet": "$subcategory.name"}
            }},
            {"$sort": {"total_sales": -1}}
        ]
        
        results = list(orders_collection.aggregate(pipeline))
        total_sales = sum(result.get("total_sales", 0) for result in results)
        
        categories = []
        for i, result in enumerate(results):
            convert_objectids_to_strings(result)
            sales = result.get("total_sales", 0)
            
            categories.append({
                "rank": i + 1,
                "category_name": result.get("category_name", "Uncategorized"),
                "total_sales": round(sales, 2),
                "units_sold": result.get("units_sold", 0),
                "percentage": round((sales / total_sales * 100), 2) if total_sales > 0 else 0,
                "subcategories": [sub for sub in result.get("subcategories", []) if sub][:5]
            })
        
        return {"top_selling_categories": categories}
        
    except Exception as e:
        logger.exception(f"Failed to get categories for store {store_id}")
        raise DatabaseConnectionError(f"Failed to get categories: {str(e)}")

def get_unsold_products_data(products_collection, orders_collection, categories_collection, units_collection, taxes_collection, store_id: str, days: int = 30) -> Dict[str, Any]:
    """Get unsold products with comprehensive analysis"""
    try:
        store_obj_id = validate_store_id(store_id)
        start_date = datetime.now() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"seller": store_obj_id, "status": "APPROVED", "stage": "ACTIVATE"}},
            {"$lookup": {
                "from": "orders",
                "let": {"product_id": "$_id"},
                "pipeline": [
                    {"$match": {"$and": [{"createdAt": {"$gte": start_date}}, {"status": {"$nin": ["ABANDONED", "CANCELLED"]}}]}},
                    {"$unwind": "$items"},
                    {"$match": {"$expr": {"$eq": ["$items._id", "$$product_id"]}}}
                ],
                "as": "recent_sales"
            }},
            {"$match": {"recent_sales": {"$size": 0}}},
            {"$lookup": {"from": "categories", "localField": "category", "foreignField": "_id", "as": "category_info"}},
            {"$lookup": {"from": "units", "localField": "unit", "foreignField": "_id", "as": "unit_info"}},
            {"$lookup": {"from": "taxes", "localField": "tax", "foreignField": "_id", "as": "tax_info"}},
            {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$unit_info", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$tax_info", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "ProductName": 1, "stockQuantity": 1, "mrpPrice": 1, "offerPrice": 1, "createdAt": 1,
                "category_name": "$category_info.name",
                "unit_name": "$unit_info.name",
                "tax_rate": "$tax_info.rate"
            }},
            {"$sort": {"createdAt": 1}}
        ]
        
        results = list(products_collection.aggregate(pipeline))
        
        unsold_products = []
        total_value = 0
        
        for i, result in enumerate(results):
            convert_objectids_to_strings(result)
            
            days_old = (datetime.now() - result["createdAt"]).days if result.get("createdAt") else 0
            stock = int(result.get("stockQuantity", 0))
            price = float(result.get("offerPrice", 0))
            stock_value = stock * price
            total_value += stock_value
            
            urgency = "low"
            if days_old > 60:
                urgency = "critical"
            elif days_old > 30:
                urgency = "high"
            elif days_old > 15:
                urgency = "medium"
            
            unsold_products.append({
                "rank": i + 1,
                "product_id": result.get("_id", ""),
                "product_name": result.get("ProductName", "Unknown"),
                "category": result.get("category_name", "Uncategorized"),
                "unit": result.get("unit_name", "Unit"),
                "stock_quantity": stock,
                "offer_price": round(price, 2),
                "stock_value": round(stock_value, 2),
                "days_in_inventory": days_old,
                "urgency": urgency,
                "tax_rate": round(float(result.get("tax_rate", 0)), 2)
            })
        
        return {
            "unsold_products": unsold_products,
            "total_products": len(unsold_products),
            "total_stock_value": round(total_value, 2),
            "critical_count": len([p for p in unsold_products if p["urgency"] == "critical"]),
            "high_count": len([p for p in unsold_products if p["urgency"] == "high"])
        }
        
    except Exception as e:
        logger.exception(f"Failed to get unsold products for store {store_id}")
        raise DatabaseConnectionError(f"Failed to get unsold products: {str(e)}")

def get_store_performance_data(sellers_collection, orders_collection, sellerpayouttransactions_collection, store_id: str, period: int = 30) -> Dict[str, Any]:
    """Get comprehensive store performance"""
    try:
        store_obj_id = validate_store_id(store_id)
        start_date = datetime.now() - timedelta(days=period)

        store_info = sellers_collection.find_one(
            {"_id": store_obj_id},
            {"storeName": 1, "storeContactName": 1, "payoutBalance": 1}
        )
        
        if not store_info:
            raise StoreNotFoundError(store_id)

        orders = list(orders_collection.find({
            "seller": store_obj_id,
            "createdAt": {"$gte": start_date}
        }))
        
        total_orders = len(orders)
        completed = len([o for o in orders if o.get("status") == "COMPLETED"])
        cancelled = len([o for o in orders if o.get("status") in ["CANCELLED", "ABANDONED"]])
        pending = total_orders - completed - cancelled
        
        total_revenue = sum(float(o.get("total", 0)) for o in orders)

        payout_stats = list(sellerpayouttransactions_collection.find({
            "seller": store_id,
            "createdAt": {"$gte": start_date.isoformat()}
        }))
        
        total_commission = sum(float(p.get("amount", 0)) for p in payout_stats)
        
        convert_objectids_to_strings(store_info)
        
        return {
            "store_info": {
                "store_name": store_info.get("storeName", "Unknown Store"),
                "contact_name": store_info.get("storeContactName", ""),
                "payout_balance": round(float(store_info.get("payoutBalance", 0)), 2)
            },
            "performance_metrics": {
                "total_orders": total_orders,
                "completed_orders": completed,
                "pending_orders": pending,
                "cancelled_orders": cancelled,
                "total_revenue": round(total_revenue, 2),
                "completion_rate": round((completed / total_orders * 100), 2) if total_orders > 0 else 0,
                "average_order_value": round((total_revenue / total_orders), 2) if total_orders > 0 else 0,
                "total_commission": round(total_commission, 2),
                "payout_transactions": len(payout_stats)
            }
        }
        
    except Exception as e:
        logger.exception(f"Failed to get performance for store {store_id}")
        raise DatabaseConnectionError(f"Failed to get performance: {str(e)}")




#Added by sanjeevan

def get_low_stock_products(
    products_collection,
    categories_collection,
    units_collection,
    store_id: str
):
    """Return products that are unavailable (availabilityStatus=False)."""
    try:
        store_obj_id = validate_store_id(store_id)

        query = {
            "seller": store_obj_id,
            "availabilityStatus": False
        }

        cursor = products_collection.find(query)

        low_stock_products = []

        for prod in cursor:
            convert_objectids_to_strings(prod)

            category = categories_collection.find_one(
                {"_id": prod.get("category")}
            ) or {}

            unit = units_collection.find_one(
                {"_id": prod.get("unit")}
            ) or {}

            low_stock_products.append({
                "product_id": prod.get("_id", "")
            })

        return {"low_stock_products": low_stock_products}

    except Exception as e:
        logger.exception(f"Failed to get low-stock products for store {store_id}")
        raise DatabaseConnectionError(f"Failed to fetch low-stock products: {str(e)}")
    

