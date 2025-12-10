from itertools import count
import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models import (
    StoresResponse, QueryRequest, QueryResponse, PopularSearchesResponse,
    RedisSessionsResponse, SessionByIdResponse
)
from app.services import StoreService, AnalyticsService, QueryService, AIService

logger = logging.getLogger(__name__)
router = APIRouter()

# Store endpoints
# @router.get("/api/stores", response_model=StoresResponse, tags=["Stores"])
# async def get_stores():
#     """Get all active stores"""
#     try:
#         return StoreService.get_all_stores()
#     except Exception as e:
#         logger.exception("Failed to get stores")
#         raise HTTPException(status_code=500, detail="Failed to get stores")

# Analytics endpoints


@router.get("/api/analytics/top-selling-products/{store_id}", tags=["Analytics"])
async def get_top_products(
    store_id: str,
    limit: int = Query(10, ge=1, le=50),
    period: int = Query(30, ge=1, le=365)
):
    """Get your best-selling products with comprehensive data"""
    try:
        return AnalyticsService.get_top_products(store_id, limit, period)
    except Exception as e:
        logger.exception("Failed to get top products")
        raise HTTPException(status_code=500, detail="Failed to get top products")

@router.get("/api/analytics/get_low_selling_products/{store_id}", tags=["Analytics"])
async def get_low_selling_products(
    store_id: str,
    limit: int = Query(10, ge=1, le=50),
    period: int = Query(30, ge=1, le=365)
):
    """Get your best-selling products with comprehensive data"""
    try:
        return AnalyticsService.get_low_selling_products(store_id, limit, period)
    except Exception as e:
        logger.exception("Failed to get top products")
        raise HTTPException(status_code=500, detail="Failed to get top products")



# @router.get("/api/analytics/popular-searches/{store_id}", response_model=PopularSearchesResponse, tags=["Analytics"])
# async def get_popular_searches(
#     store_id: str,
#     limit: int = Query(10, ge=1, le=50),
#     days: int = Query(30, ge=1, le=365)
# ):
#     """Get popular searches: Sno, contextual category (dishbased), search query"""
#     try:
#         return AnalyticsService.get_popular_searches(store_id, limit, days)
#     except Exception as e:
#         logger.exception("Failed to get search data")
#         raise HTTPException(status_code=500, detail="Failed to get search data")

@router.get("/api/analytics/top-selling-categories/{store_id}", tags=["Analytics"])
async def get_categories(
    store_id: str,
    period: int = Query(30, ge=1, le=365)
):
    """Get your top-selling categories with subcategory info"""
    try:
        return AnalyticsService.get_categories(store_id, period)
    except Exception as e:
        logger.exception("Failed to get categories")
        raise HTTPException(status_code=500, detail="Failed to get categories")

@router.get("/api/analytics/unsold-products/{store_id}", tags=["Analytics"])
async def get_unsold_products(
    store_id: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get products that need attention with detailed analysis"""
    try:
        return AnalyticsService.get_unsold_products(store_id, days)
    except Exception as e:
        logger.exception("Failed to get unsold products")
        raise HTTPException(status_code=500, detail="Failed to get unsold products")

@router.get("/api/analytics/store-performance/{store_id}", tags=["Analytics"])
async def get_store_performance(
    store_id: str,
    period: int = Query(30, ge=1, le=365)
):
    """Get your comprehensive store performance"""
    try:
        return AnalyticsService.get_performance(store_id, period)
    except Exception as e:
        logger.exception("Failed to get performance data")
        raise HTTPException(status_code=500, detail="Failed to get performance data")

# @router.post("/query", response_model=QueryResponse, tags=["Chat"])
# # async def search_with_ai_and_redis(request: QueryRequest):
#     """
#     AI Search with Redis Session Tracking:
#     1. Process user query intelligently
#     2. Search database for relevant results (products/categories)
#     3. Generate natural AI response using GPT
#     4. Save session (clean_id, store_id, query, response) in Redis with 24h expiry
#     """
#     try:
#         return QueryService.process_query(request)
#     except Exception as e:
#         logger.exception("Enhanced AI search failed")
#         raise HTTPException(status_code=500, detail="AI Search temporarily unavailable")

# @router.get("/api/sessions", response_model=RedisSessionsResponse, tags=["Redis Sessions"])
# async def get_redis_sessions(
#     store_id: Optional[str] = Query(None, description="Filter by store ID"),
#     limit: int = Query(50, ge=1, le=100, description="Maximum sessions to return")
# ):
#     """
#     View stored Redis sessions with optional store filtering
    
#     Features:
#     - View all stored search sessions
#     - Filter by specific store ID
#     - Shows session expiry information
#     - Pagination support
#     """
#     try:
#         return QueryService.get_redis_sessions(store_id, limit)
#     except Exception as e:
#         logger.exception("Failed to get Redis sessions")
#         raise HTTPException(status_code=500, detail="Cannot retrieve sessions")

# @router.get("/api/sessions/{session_id}", response_model=SessionByIdResponse, tags=["Redis Sessions"])
# async def get_session_by_id(session_id: str):
#     """
#     Get specific session details by session ID
    
#     Features:
#     - Retrieve complete session information
#     - Shows TTL and expiry details
#     - Error handling for missing sessions
#     """
#     try:
#         session_data = QueryService.get_session_by_id(session_id)
        
#         if "error" in session_data:
#             raise HTTPException(status_code=404, detail=session_data["error"])
        
#         return session_data
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.exception("Failed to get session")
#         raise HTTPException(status_code=500, detail="Cannot retrieve session")


@router.get("/stores/{store_id}/recommendations/discounts", tags=["AI Features"])
async def get_discount_recommendations(store_id: str):
    """Get AI discount recommendations using GPT"""
    try:
        return AIService.get_discount_recommendations(store_id)
    except Exception as e:
        logger.exception("Failed to get discount recommendations")
        raise HTTPException(status_code=500, detail="Cannot get recommendations")






#-------------------------------------------------- NEW ENDPOINT FROM DUMILU------------------------




from bson import ObjectId
from app.database import db , supabase_client 

@router.get("/api/analytics/total-products/{store_id}", tags=["Analytics"])
def get_product_count(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # ⬇️ Apply status filter if provided
        if status:
            match_stage["status"] = status

        # ⬇️ Apply date filters based on createdAt
        if date_from or date_to:
            date_filter = {}

            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)

            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)

            match_stage["createdAt"] = date_filter

        # Count documents with filters applied
        count = db.products.count_documents(match_stage)

        return {
            "store_id": store_id,
            "total_products": count,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch product count: {str(e)}"
        )
@router.get("/api/analytics/total-sales/{store_id}", tags=["Analytics"])
def get_total_sales(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # ⬇️ Apply status filter if provided
        if status:
            match_stage["status"] = status

        # ⬇️ Apply date filters
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)

            match_stage["createdAt"] = date_filter

        count = db.orders.count_documents(match_stage)

        return {
            "store_id": store_id,
            "total_sales": count,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales count: {str(e)}")
    
@router.get("/api/analytics/total-revenue/{store_id}", tags=["Analytics"])
def get_total_revenue(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)   # COMPLETED / CANCELLED / PENDING etc.
):
    try:
        # Base match
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # Apply status filter
        if status:
            match_stage["status"] = status

        # Apply date filters
        if date_from or date_to:
            date_filter = {}

            if date_from:
                # Automatically parses microseconds
                date_filter["$gte"] = datetime.fromisoformat(date_from)

            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)

            match_stage["createdAt"] = date_filter

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
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch revenue: {str(e)}")


@router.get("/api/analytics/monthly-revenue/{store_id}", tags=["Analytics"])
def get_monthly_revenue(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
):
    try:
        # Base filters
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # Status filter
        if status:
            match_stage["status"] = status

        # Date filters
        if date_from or date_to:
            date_filter = {}

            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)

            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)

            match_stage["createdAt"] = date_filter

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
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch monthly revenue: {str(e)}")
    


@router.get("/api/analytics/total-customers/{store_id}", tags=["Analytics"])
def get_total_customers(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
):
    try:
        match_stage = {
            "seller": ObjectId(store_id)
        }

        # Status filter (COMPLETED / CANCELLED / RETURNED / etc.)
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

        total = db.orders.count_documents(match_stage)

        return {
            "store_id": store_id,
            "total_customers": total,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch total customers: {str(e)}")
    

@router.get("/api/analytics/unique-customers/{store_id}", tags=["Analytics"])
def get_unique_customers(
    store_id: str,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
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
                "status": status
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch unique customers: {str(e)}")
    
    
@router.get("/stores/{store_id}/products/substitutions", tags=["AI Features"])
async def get_product_substitutes(
    store_id: str,
    top_n: int = Query(5, ge=1, le=5)
):
    
    """Get AI-powered alternative products using GPT"""
    try:
        product_data = AnalyticsService.get_low_stock_product(store_id)
        product_ids = [item["product_id"] for item in product_data.get("low_stock_products", [])]

        results = []
        for pid in product_ids:
            substitutes = AIService.get_product_substitutes(store_id, pid, top_n)
            results.append({
                "product_id": pid,
                "substitutes": substitutes
            })

        return {"results": results}
    except Exception as e:
        logger.exception("Failed to get product substitutes")
        raise HTTPException(status_code=500, detail="Cannot get alternatives")





# @router.get("/api/analytics/sales-by-time-period/{store_id}", tags=["Analytics"])
# def get_sales_by_time_period(store_id: str):
#     try:
#         store_obj_id = ObjectId(store_id)

#         pipeline = [
#             {
#                 "$match": {
#                     "seller": store_obj_id,
#                     "status": "COMPLETED"
#                 }
#             },
#             {
#                 "$project": {
#                     "hour": {"$hour": "$createdAt"},
#                     "amount": "$amountReceived"
#                 }
#             },
#             {
#                 "$group": {
#                     "_id": {
#                         "$switch": {
#                             "branches": [
#                                 {
#                                     "case": {"$and": [{"$gte": ["$hour", 6]}, {"$lt": ["$hour", 12]}]},
#                                     "then": "Morning"
#                                 },
#                                 {
#                                     "case": {"$and": [{"$gte": ["$hour", 12]}, {"$lt": ["$hour", 18]}]},
#                                     "then": "Afternoon"
#                                 },
#                                 {
#                                     "case": {"$and": [{"$gte": ["$hour", 18]}, {"$lt": ["$hour", 21]}]},
#                                     "then": "Evening"
#                                 }
#                             ],
#                             "default": "Night"   # 21–24 and 0–6
#                         }
#                     },
#                     "orders_count": {"$sum": 1},
#                     "total_revenue": {"$sum": "$amount"}
#                 }
#             },
#             {"$sort": {"_id": 1}}
#         ]

#         data = list(db.orders.aggregate(pipeline))

#         return {
#             "store_id": store_id,
#             "sales_by_time_period": data
#         }

#     except Exception:
#         raise HTTPException(500, "Failed to fetch time-period sales")
    

from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
@router.get("/api/analytics/recent-orders/{store_id}", tags=["Analytics"])
def get_recent_orders(
    store_id: str,
    page: int = 1,
    limit: int = 10,
    status: str = None,
    order_type: str = None,
    date_from: str = None,
    date_to: str = None,
    search: str = None  # 🆕 NEW SEARCH PARAMETER
):
    try:
        store_obj_id = ObjectId(store_id)
        
        # Build match conditions
        match_conditions = {"seller": store_obj_id}
        
        # Optional filters
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

        # 🆕 ADD TEXT SEARCH FILTER
        if search:
            search_pattern = {"$regex": search, "$options": "i"}  # case-insensitive
            match_conditions["$or"] = [
                {"orderNo": search_pattern},
                {"customer.customerName": search_pattern},
                {"customer.phoneNumber": search_pattern}
            ]

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
                "search": search  # 🆕 Include in response
            },
            "orders": orders
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch recent orders: {str(e)}")
    

@router.get("/api/analytics/Top_Dish_Searches/{store_id}", tags=["Analytics"])
def get_top_dish_searches(store_id: str):
    try:
        # 1️⃣ Fetch relevant rows from raw_data
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

        # 2️⃣ Collect unique product_ids
        product_ids = list({row["product_id"] for row in raw_data if row.get("product_id")})

        if not product_ids:
            return {"store_id": store_id, "data": raw_data, "message": "No product_id found in searches"}
        

        # 3️⃣ Fetch product names from product_details
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

        # 4️⃣ Merge product_name into raw_data
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
load_dotenv("Buy2CashStoreMang/config.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

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


@router.get("/api/analytics/top-stock-alerts/{store_id}", tags=["Analytics"])
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
