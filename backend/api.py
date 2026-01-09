from itertools import count
import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()



#-------------------------------------------------- ALL KPIS CARD ENDPOINTS ------------------------




from bson import ObjectId
from database import db , supabase_client 
@router.get("/api/analytics/total-products/{store_id}", tags=["Analytics"])
def get_product_count(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        # -------------------------
        # Match WITH date filters
        # -------------------------
        match_stage = {
            "seller": ObjectId(store_id)
        }

        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        if category_id:
            match_stage["$or"] = [
                {"category": ObjectId(category_id)},
                {"subCategory": ObjectId(category_id)}
            ]

        filtered_count = db.products.count_documents(match_stage)


        return {
            "store_id": store_id,
            "products_count": filtered_count,     
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch product counts: {str(e)}"
        )



@router.get("/api/analytics/total-sales/{store_id}", tags=["Analytics"])
def get_total_sales(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        # -------------------------
        # WITH date filters
        # -------------------------
        match_stage = {
            "seller": ObjectId(store_id)
        }

        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [p["_id"] for p in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        filtered_count = db.orders.count_documents(match_stage)

        

        return {
            "store_id": store_id,
            "sales_count": filtered_count,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales counts: {str(e)}")


@router.get("/api/analytics/total-revenue/{store_id}", tags=["Analytics"])
def get_total_revenue(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }
        
        if status:
            match_stage["status"] = status
            
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        # If category filter is provided
        if category_id:
            # Step 1: Get all product IDs for this category
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            
            # Step 2: Add items array filter to match stage
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "totalRevenue": {"$sum": "$total"}
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))
        revenue = result[0]["totalRevenue"] if result else 0

        return {
            "store_id": store_id,
            "total_revenue": revenue,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch revenue: {str(e)}")

DEFAULT_MONTHS_WINDOW_DAYS = 365  # last 12 months


@router.get("/api/analytics/avg-order-value/{store_id}", tags=["Analytics"])
def get_avg_order_value(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        match_stage = {"seller": ObjectId(store_id)}

        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [p["_id"] for p in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "totalOrders": {"$sum": 1},
                    "totalRevenue": {"$sum": "$total"}
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))
        total_orders = result[0]["totalOrders"] if result else 0
        total_revenue = result[0]["totalRevenue"] if result else 0
        avg_order_value = (total_revenue / total_orders) if total_orders else 0

        return {
            "store_id": store_id,
            "avg_order_value": avg_order_value,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch avg order value: {str(e)}")


@router.get("/api/analytics/avg-sales-per-month/{store_id}", tags=["Analytics"])
def get_avg_sales_per_month(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        match_stage = {"seller": ObjectId(store_id)}

        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [p["_id"] for p in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "month": {"$month": "$createdAt"}
                    },
                    "sales": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {
                "$group": {
                    "_id": None,
                    "months_count": {"$sum": 1},
                    "total_sales": {"$sum": "$sales"},
                    "avg_sales_per_month": {"$avg": "$sales"},
                    "by_month": {
                        "$push": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "sales": "$sales"
                        }
                    }
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))
        if not result:
            return {
                "store_id": store_id,
                "avg_sales_per_month": 0,
                "months_count": 0,
                "total_sales": 0,
                "by_month": [],
                "filters_applied": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "status": status,
                    "category_id": category_id
                }
            }

        row = result[0]
        return {
            "store_id": store_id,
            "avg_sales_per_month": row.get("avg_sales_per_month", 0),
            "months_count": row.get("months_count", 0),
            "total_sales": row.get("total_sales", 0),
            "by_month": row.get("by_month", []),
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch avg sales/month: {str(e)}")




@router.get("/api/analytics/total-customers/{store_id}", tags=["Analytics"])
def get_total_customers(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }
        
        if status:
            match_stage["status"] = status

        # Date range filter using createdAt
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        total = db.orders.count_documents(match_stage)

        return {
            "store_id": store_id,
            "total_customers": total,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch total customers: {str(e)}")
    

@router.get("/api/analytics/unique-customers/{store_id}", tags=["Analytics"])
def get_unique_customers(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        # Base match
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # Status filter
        if status:
            match_stage["status"] = status

        # Date range filter
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        # If category filter is provided
        if category_id:
            # Step 1: Get all product IDs for this category
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            
            # Step 2: Add items array filter to match stage
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "uniqueCustomers": {"$addToSet": "$customer.id"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "count": {"$size": "$uniqueCustomers"}
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))
        count = result[0]["count"] if result else 0

        return {
            "store_id": store_id,
            "unique_customers": count,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch unique customers: {str(e)}")
    

@router.get("/api/analytics/top-customers/{store_id}", tags=["Analytics"])
def get_top_customers(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }

        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter

        # Category filter (same approach as your working endpoints)
        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [p["_id"] for p in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$customer.id",
                    "customerName": {"$first": "$customer.customerName"},
                    "phoneNumber": {"$first": "$customer.phoneNumber"},
                    "total_spent": {"$sum": "$total"},
                    "orders_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_spent": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "customer_id": {"$toString": "$_id"},
                    "customerName": 1,
                    "phoneNumber": 1,
                    "total_spent": 1,
                    "orders_count": 1
                }
            }
        ]

        top_customers = list(db.orders.aggregate(pipeline))

        return {
            "store_id": store_id,
            "top_customer": top_customers[0] if top_customers else None,
            # "top_customers": top_customers,
            # "filters_applied": {
            #     "date_from": date_from,
            #     "date_to": date_to,
            #     "status": status,
            #     "category_id": category_id,
            #     "limit": limit
            # }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top customers: {str(e)}")



#---------------------------------------------------------All Graph ENdpoints HERE ----------------------------------------------



@router.get("/api/analytics/monthly-revenue/{store_id}", tags=["Analytics"])
def get_monthly_revenue(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }
        if status:
            match_stage["status"] = status

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter
        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "month": {"$month": "$createdAt"}
                    },
                    "totalRevenue": {"$sum": "$total"}
                }
            },
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))

        formatted = [
            {
                "year": item["_id"]["year"],
                "month": item["_id"]["month"],
                "total_revenue": item["totalRevenue"]
            }
            for item in result
        ]

        return {
            "store_id": store_id,
            "monthly_revenue": formatted,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch monthly revenue: {str(e)}")







@router.get("/api/analytics/sales-by-time-period/{store_id}", tags=["Analytics"])
def get_sales_by_time_period(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None)
):
    try:
        store_obj_id = ObjectId(store_id)

        match_stage = {
            "seller": store_obj_id
        }
        if status:
            match_stage["status"] = status
        else:
            match_stage["status"] = "COMPLETED"
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter
        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {
                "$project": {
                    "hour": {"$hour": "$createdAt"},
                    "amount": "$amountReceived"
                }
            },
            {
                "$group": {
                    "_id": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {"$and": [{"$gte": ["$hour", 6]}, {"$lt": ["$hour", 12]}]},
                                    "then": "Morning"
                                },
                                {
                                    "case": {"$and": [{"$gte": ["$hour", 12]}, {"$lt": ["$hour", 18]}]},
                                    "then": "Afternoon"
                                },
                                {
                                    "case": {"$and": [{"$gte": ["$hour", 18]}, {"$lt": ["$hour", 21]}]},
                                    "then": "Evening"
                                }
                            ],
                            "default": "Night"
                        }
                    },
                    "orders_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$amount"}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        data = list(db.orders.aggregate(pipeline))

        return {
            "store_id": store_id,
            "sales_by_time_period": data,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status if status else "COMPLETED",
                "category_id": category_id
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch time-period sales: {str(e)}")
    

@router.get("/api/analytics/products-by-category/{store_id}", tags=["Analytics"])
def get_products_by_category(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None, description="Order status filter"),
    category_id: str = Query(None, description="Filter by specific category")
):
    try:
        store_obj_id = ObjectId(store_id)
        
        match_stage = {
            "seller": store_obj_id
        }
        
        if status:
            match_stage["status"] = status
        
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_stage["createdAt"] = date_filter
        
        # Add category filter if provided
        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            match_stage["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_stage},
            {"$unwind": "$items"},
            {
                "$lookup": {
                    "from": "products",
                    "localField": "items._id",
                    "foreignField": "_id",
                    "as": "product_info"
                }
            },
            {"$unwind": "$product_info"},
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "product_info.category",
                    "foreignField": "_id",
                    "as": "category_info"
                }
            },
            {"$unwind": "$category_info"},
            {
                "$group": {
                    "_id": "$product_info.category",
                    "category_name": {"$first": "$category_info.name"},
                    "product_count": {"$addToSet": "$items._id"},
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$items.subTotal"},
                    "total_quantity": {"$sum": "$items.quantity"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "category_id": {"$toString": "$_id"},
                    "category_name": 1,
                    "product_count": {"$size": "$product_count"},
                    "order_count": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "total_stock_value": {"$round": ["$total_revenue", 2]},
                    "total_quantity": 1
                }
            },
            {"$sort": {"order_count": -1}}
        ]

        result = list(db.orders.aggregate(pipeline))

        return {
            "store_id": store_id,
            "total_categories": len(result),
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status,
                "category_id": category_id
            },
            "categories_distribution": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch category distribution: {str(e)}")

        

@router.get("/api/analytics/top-selling-products/{store_id}", tags=["Analytics"])
def get_top_selling_products(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None),
    category_id: str = Query(None),
    limit: int = Query(5, description="Number of top products to return")
):
    try:
        store_obj_id = ObjectId(store_id)
        match_conditions = {"seller": store_obj_id}
        if status:
            match_conditions["status"] = status
        # else:
        #     match_conditions["status"] = "COMPLETED"
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_conditions["createdAt"] = date_filter

        if category_id:
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            match_conditions["items._id"] = {"$in": product_id_list}

        pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items._id",
                    "product_name": {"$first": "$items.productName"},
                    "total_quantity_sold": {"$sum": "$items.quantity"},
                    "total_orders": {"$sum": 1},
                    "total_revenue": {"$sum": "$items.subTotal"},
                    "product_image": {"$first": {"$arrayElemAt": ["$items.image", 0]}}
                }
            },
            {"$sort": {"total_quantity_sold": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "product_id": {"$toString": "$_id"},
                    "product_name": 1,
                    "total_quantity_sold": 1,
                    "total_orders": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "product_image": 1
                }
            }
        ]

        result = list(db.orders.aggregate(pipeline))

        return {
            "store_id": store_id,
            "top_products_count": len(result),
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status if status else "COMPLETED",
                "category_id": category_id,
                "limit": limit
            },
            "top_selling_products": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top selling products: {str(e)}")


from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

#-------------------------------------------------- ADDED RECENT ORDERS --------------------------------------------------------------------


@router.get("/api/analytics/recent-orders/{store_id}", tags=["Analytics"])
def get_recent_orders(
    store_id: str,
    page: int = 1,
    limit: int = None,
    status: str = None,
    order_type: str = None,
    date_from: str = None,
    date_to: str = None,
    search: str = None,
    category_id: str = None
):
    try:
        store_obj_id = ObjectId(store_id)
        match_conditions = {"seller": store_obj_id}
        
        if status:
            match_conditions["status"] = status
        if order_type:
            match_conditions["orderType"] = order_type
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            match_conditions["createdAt"] = date_filter

        # Text search filter
        if search:
            search_pattern = {"$regex": search, "$options": "i"}  # case-insensitive
            match_conditions["$or"] = [
                {"orderNo": search_pattern},
                {"customer.customerName": search_pattern},
                {"customer.phoneNumber": search_pattern}
            ]

        # Category filter
        if category_id:
            # Get all product IDs for this category
            product_ids = db.products.find(
                {"category": ObjectId(category_id)},
                {"_id": 1}
            )
            product_id_list = [product["_id"] for product in product_ids]
            
            # Add items array filter to match conditions
            match_conditions["items._id"] = {"$in": product_id_list}

        # Calculate skip for pagination
        skip = (page - 1) * limit

        pipeline = [
            {"$match": match_conditions},
            {"$sort": {"createdAt": -1}},
            {
                "$facet": {
                    "orders": [
                        {"$skip": skip},
                        {"$limit": limit},
                        {
                            "$project": {
                                "_id": 0,
                                "order_id": "$orderNo",
                                "invoice_no": "$invoiceNo",
                                "customer": {
                                    "name": "$customer.customerName",
                                    "phone": "$customer.phoneNumber"
                                },
                                "date_time": {
                                    "created": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$createdAt"}},
                                    "delivered": {
                                        "$cond": [
                                            {"$ifNull": ["$deliveredAt", False]},
                                            {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$deliveredAt"}},
                                            None
                                        ]
                                    }
                                },
                                "items": {
                                    "$map": {
                                        "input": "$items",
                                        "as": "item",
                                        "in": {
                                            "name": "$$item.productName",
                                            "quantity_info": "$$item.Quantity",
                                            "quantity": "$$item.quantity",
                                            "price": "$$item.offerPrice",
                                            "subtotal": "$$item.subTotal"
                                        }
                                    }
                                },
                                "items_count": {"$size": "$items"},
                                "amount": {
                                    "subtotal": "$subTotal",
                                    "total": "$total",
                                    "amount_received": "$amountReceived",
                                    "charges": "$charges"
                                },
                                "delivery_info": {
                                    "type": "$deliveryType",
                                    "pickup_address": "$shippingInfo.pickup.formatted_address",
                                    "delivery_address": "$shippingInfo.delivery.address.formatted_address",
                                    "delivery_name": "$shippingInfo.delivery.name",
                                    "delivery_phone": "$shippingInfo.delivery.alternativePhoneNumber",
                                    "distance": "$shippingInfo.distanceBetweenStoreAndCustomer",
                                    "driver": {
                                        "name": "$shippingInfo.driver.details.driver_name",
                                        "mobile": "$shippingInfo.driver.details.mobile"
                                    }
                                },
                                "status": "$status",
                                "category": "$orderType",
                                "payment_method": "$paymentMethod",
                                "time_duration": "$timeDuration"
                            }
                        }
                    ],
                    "total_count": [
                        {"$count": "count"}
                    ]
                }
            }
        ]
        
        result = list(db.orders.aggregate(pipeline))
        
        orders = result[0]["orders"] if result else []
        total_count = result[0]["total_count"][0]["count"] if result and result[0]["total_count"] else 0
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "store_id": store_id,
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "filters_applied": {
                "status": status,
                "order_type": order_type,
                "date_from": date_from,
                "date_to": date_to,
                "search": search,
                "category_id": category_id
            },
            "orders": orders
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch recent orders: {str(e)}")
    



#-------------------------------------------------- Supabase DATA FETCHING --------------------------------------------------------------------

@router.get("/api/analytics/top-dish-searches/{store_id}", tags=["Analytics"])
def get_top_dish_searches(store_id: str):
    try:
        raw_resp = (
            supabase_client
            .from_("raw_data")
            .select("query, dishbased, cuisinebased, dietarybased, timebased, timestamp, product_id")
            .eq("store_id", store_id)
            .execute()
        )


        raw_data = raw_resp.data

        if not raw_data:
            return {"store_id": store_id, "data": [], "message": "No search data found"}
        product_ids = list({row["product_id"] for row in raw_data if row.get("product_id")})

        if not product_ids:
            return {"store_id": store_id, "data": raw_data, "message": "No product_id found in searches"}
        product_resp = (
            supabase_client
            .from_("product_details")
            .select("product_id, product_name")
            .in_("product_id", product_ids)
            .execute()
        )


        from collections import defaultdict

        product_map = defaultdict(list)

        for p in product_resp.data:
            product_map[p["product_id"]].append(p["product_name"])
        final_data = []
        for row in raw_data:
            final_data.append({
                **row,
                "product_name": product_map.get(row["product_id"], None)
            })

        return {
            "store_id": store_id,
            "count": len(final_data),
            "data": final_data
        }

    except Exception as e:
        logger.exception("Error fetching top dish searches")
        raise HTTPException(status_code=500, detail=str(e))
    



#-------------------------------------------------- ADDED AI CLIENT LATER OPTIMIZE IT ------------------------



import json
from openai import OpenAI
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv(".env")

AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini"  # Add this to your .env
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

client = AzureOpenAI(
    api_key=AZURE_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=AZURE_API_VERSION
)
def recommend_for_product(item: dict):
    prompt = f"""
You are a retail analytics strategist.

Given the following product data:
- Product Name: {item.get('ProductName')}
- MRP Price: {item.get('mrpPrice')}
- Offer Price: {item.get('offerPrice')}
- POS Price: {item.get('posPrice')}
- Stock Quantity: {item.get('stockQuantity')}

TASK:
1. Analyse pricing, demand likelihood, and stock levels.
2. Recommend ONE very specific action to improve sales or optimize inventory.
3. Provide a short, crisp reasoning.

Output strictly in JSON with keys: recommendation, reasoning.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={"type": "json_object"},  # ENFORCE VALID JSON
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        return json.loads(raw) # type: ignore

    except Exception as e:
        print("LLM ERROR RAW:", response)
        print("Exception:", e)
        return {
            "recommendation": "Unable to generate recommendation.",
            "reasoning": "LLM JSON parsing failed."
        }


@router.get("/api/analytics/top-stock-alerts/{store_id}", tags=["AI Analytics"])
def get_top_stock_alerts(store_id: str):
    try:
        store_obj_id = ObjectId(store_id)

        pipeline = [
            {
                "$match": {
                    "seller": store_obj_id
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "ProductName": 1,
                    "stockQuantity": 1,
                    "updatedAt": 1,
                    "mrpPrice": 1,
                    "offerPrice": 1,
                    "posPrice": 1
                }
            },
            {
                "$sort": {
                    "stockQuantity": -1,       # highest stock first
                    "updatedAt": 1            # oldest update first
                }
            },
            { "$limit": 5 }
        ]

        data = list(db.products.aggregate(pipeline))
        
        
        enriched = []
        for item in data:
            reco = recommend_for_product(item)
            enriched.append({
                **item,
                "recommendation": reco["recommendation"],
                "reasoning": reco["reasoning"]
            })

        return {
            "store_id": store_id,
            "Ai_recommendations": enriched,
            "data": data
        }


    except Exception:
        raise HTTPException(500, "Failed to fetch stock alerts")









# ============================================================================

# ============================================================================

# ============================================================================

import os
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from bson import ObjectId
from openai import OpenAI

# ============================================================================
# AI PROMPTS FOR SUBSTITUTIONS
# ============================================================================

SUBSTITUTION_SYSTEM_PROMPT = """You are an expert in product recommendations for grocery stores. 
Analyze the given product and alternatives to suggest the best substitutions for customers.
Focus on customer satisfaction, similar value, and business benefit."""

SUBSTITUTION_USER_PROMPT = """Suggest the best {top_n} product alternatives:

Original Product: {product_info}
Available Options: {alternatives}

Return JSON array with {top_n} best substitutes:
[{{"product_id": "id", "product_name": "name", "similarity_score": 0.9, "price_difference": -5, "reason": "why good substitute"}}]

Consider category similarity, price range, and customer acceptance."""

MINI_MODEL_NAME = "gpt-4o-mini"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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
        raise ValueError(f"Invalid store ID: {store_id}")


def is_ai_available(openai_client) -> bool:
    """Check if AI client is available"""
    return openai_client is not None


def initialize_openai_client():
    """Initialize OpenAI client"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            logger.info("AI assistant ready with GPT-4o mini")
            return client
        except Exception as e:
            logger.warning(f"AI setup failed: {str(e)}")
            return None
    else:
        logger.warning("OpenAI API key not configured")
        return None

# ============================================================================
# CORE SUBSTITUTION FUNCTIONS
# ============================================================================

def simple_substitutes(product_data: Dict, similar_products: List[Dict], top_n: int) -> List[Dict]:
    """Simple substitutes without AI - fallback function"""
    substitutes = []
    original_price = product_data.get("offerPrice", 0)
    
    for i, product in enumerate(similar_products[:top_n]):
        price = product.get("offerPrice", 0)
        substitutes.append({
            "product_id": str(product.get("_id", "")),
            "product_name": product.get("ProductName", "Unknown Product"),
            "similarity_score": round(0.8 - (i * 0.1), 2),
            "price_difference": round(price - original_price, 2),
            "reason": "Similar product in same category"
        })
    
    return substitutes

def suggest_substitutes(
    product_data: Dict, 
    similar_products: List[Dict], 
    top_n: int = 5,
    openai_client = None
) -> List[Dict]:
    """Suggest product alternatives using GPT"""
    if not is_ai_available(openai_client) or not similar_products:
        return simple_substitutes(product_data, similar_products, top_n)
    
    try:
        product_info = f"Product: {product_data.get('ProductName', 'Unknown')}, Price: ₹{product_data.get('offerPrice', 0)}"
        
        alternatives = []
        for prod in similar_products[:10]:
            alternatives.append({
                "name": prod.get("ProductName", "Unknown"),
                "price": prod.get("offerPrice", 0),
                "category": prod.get("category", "Unknown"),
                "id": str(prod.get("_id", ""))
            })
        
        user_prompt = SUBSTITUTION_USER_PROMPT.format(
            top_n=top_n,
            product_info=product_info,
            alternatives=json.dumps(alternatives, indent=2)
        )
        
        response = openai_client.chat.completions.create(
            model=MINI_MODEL_NAME,
            messages=[
                {"role": "system", "content": SUBSTITUTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            substitutes = json.loads(ai_response)
            if isinstance(substitutes, list):
                return substitutes[:top_n]
        except:
            pass
        
        return simple_substitutes(product_data, similar_products, top_n)
        
    except Exception as e:
        logger.exception("AI substitutes failed")
        return simple_substitutes(product_data, similar_products, top_n)


def get_product_substitutes(
    store_id: str,
    product_id: str,
    top_n: int = 5,
    products_collection = None,
    categories_collection = None,
    openai_client = None
) -> Dict[str, Any]:
    """Get product substitutes using GPT-4o mini"""
    try:
        store_obj_id = validate_store_id(store_id)
        product_obj_id = ObjectId(product_id)
        
        original = products_collection.find_one({
            "_id": product_obj_id,
            "seller": store_obj_id
        })
        logger.info(f"Original product: {original}")
        
        if not original:
            raise Exception("Product not found")
        
        similar_query = {
            "seller": store_obj_id,
            "status": "APPROVED",
            "_id": {"$ne": product_obj_id}
        }
        
        if original.get("category"):
            similar_query["category"] = original["category"]
        
        logger.info(f"Similar products query: {similar_query}")
        
        similar_products = list(products_collection.find(similar_query).limit(15))
        logger.info(f"Found {len(similar_products)} similar products")
        
        for product in similar_products:
            logger.info(f"Processing similar product: {product.get('ProductName')}, Category: {product.get('category')}")
            convert_objectids_to_strings(product)
            if product.get("category"):
                try:
                    cat_info = categories_collection.find_one({"_id": ObjectId(product["category"])})
                    product["category"] = cat_info.get("name", "Unknown") if cat_info else "Unknown"
                except:
                    product["category"] = "Unknown"
        
        substitutes = suggest_substitutes(original, similar_products, top_n, openai_client)
        
        return {
            "store_id": store_id,
            "original_product": {
                "name": original.get("ProductName", "Unknown"),
                "price": original.get("offerPrice", 0)
            },
            "substitutes": substitutes,
            "ai_model": "gpt-4o-mini"
        }
        
    except Exception as e:
        logger.exception("Failed to get substitutes")
        raise


def get_low_stock_products(
    products_collection,
    categories_collection,
    units_collection,
    store_id: str,
    limit: int = 5
) -> Dict[str, Any]:
    """Return top N products that are unavailable (availabilityStatus=False), sorted by stock quantity (lowest first)"""
    try:
        store_obj_id = validate_store_id(store_id)
        query = {
            "seller": store_obj_id,
            "availabilityStatus": False
        }

        # Sort by stock quantity ascending (lowest stock first) and limit to top N
        cursor = products_collection.find(query).sort("stockQuantity", 1).limit(limit)

        low_stock_products = []

        for prod in cursor:
            logger.info(f"Low stock product: {prod}")
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
        raise Exception(f"Failed to fetch low-stock products: {str(e)}")

@router.get("/", tags=["Health"])
def health():
    return {"status": "ok"}

@router.get("/api/analytics/quick-analysis/{store_id}", tags=["AI Analytics"])
def get_product_substitutes_for_low_stock(
    store_id: str,
    top_n: int = Query(4, ge=1, le=10, description="Number of substitute products to suggest per low stock product")
) -> Dict[str, Any]:
    """Get AI-powered alternative products for top 5 low stock items using GPT"""
    try:
        # Use database collections directly
        products_collection = db.products
        categories_collection = db.categories
        units_collection = db.units
        # Use the AzureOpenAI client that's already initialized
        openai_client = client if AZURE_KEY and AZURE_ENDPOINT else None
        
        # Get top 5 low stock products
        product_data = get_low_stock_products(
            products_collection,
            categories_collection,
            units_collection,
            store_id,
            limit=5
        )
        product_ids = [item["product_id"] for item in product_data.get("low_stock_products", [])]

        results = []
        for pid in product_ids:
            # Get top_n (default 4) substitutes for each low stock product
            substitutes = get_product_substitutes(
                store_id,
                pid,
                top_n,
                products_collection,
                categories_collection,
                openai_client
            )
            results.append({
                "product_id": pid,
                "substitutes": substitutes
            })

        return {"results": results}
    except Exception as e:
        logger.exception("Failed to get product substitutes")
        raise HTTPException(status_code=500, detail=f"Cannot get alternatives: {str(e)}")

# ============================================================================
# USAGE EXAMPLE
# ============================================================================


