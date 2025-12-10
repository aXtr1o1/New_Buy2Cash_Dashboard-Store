import logging
import uuid
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import *
from app.core import *
from app.ai_service import ai_assistant
from app.models import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

class StoreService:
    """Store service"""
    
    @staticmethod
    def get_all_stores() -> Dict[str, Any]:
        """Get all stores"""
        return get_stores_data(sellers_collection, orders_collection, products_collection)

class AnalyticsService:
    """Analytics service"""
    
    @staticmethod
    def get_top_products(store_id: str, limit: int = 10, period: int = 30) -> Dict[str, Any]:
        """Get top selling products"""
        return get_top_products_data(
            orders_collection, products_collection, categories_collection, units_collection,
            store_id, limit, period
        )
    

    @staticmethod
    def get_low_selling_products(store_id: str, limit: int = 10, period: int = 30) -> Dict[str, Any]:
        """Get top selling products"""
        return get_low_selling_products_data(orders_collection,store_id, limit, period)
    
    @staticmethod
    def get_low_stock_product(store_id: str, limit: int = 10, period: int = 30) -> Dict[str, Any]:
        """To get the low stock or zero stock product List"""
        return get_low_stock_products(products_collection, categories_collection, units_collection, store_id) # type: ignore
    
    @staticmethod
    def get_popular_searches(store_id: str, limit: int = 10, days: int = 30) -> Dict[str, Any]:
        """Get popular searches - simplified with dishbased"""
        try:
            if not supabase_client:
                return {"popular_searches": [], "message": "Search data not available"}
            
            start_date = datetime.now() - timedelta(days=days)
            
            response = (
                supabase_client.table("raw_data")
                .select("query, dishbased")
                .eq("store_id", store_id)
                .gte("timestamp", start_date.isoformat())
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            if not response.data:
                return {"popular_searches": [], "message": "No search data found"}
            
            searches = []
            for i, record in enumerate(response.data):
                query = record.get("query", "").strip()
                dishbased = record.get("dishbased", [])
                
                if query:
                    searches.append({
                        "sno": i + 1,
                        "contextual_category": ", ".join(dishbased) if dishbased else "",
                        "search_query": query
                    })
            
            return {"popular_searches": searches}
            
        except Exception as e:
            logger.exception("Failed to get popular searches")
            return {"popular_searches": [], "error": str(e)}
    
    @staticmethod
    def get_categories(store_id: str, period: int = 30) -> Dict[str, Any]:
        """Get top categories"""
        return get_categories_data(
            orders_collection, categories_collection, subcategories_collection, store_id, period
        )
    
    @staticmethod
    def get_unsold_products(store_id: str, days: int = 30) -> Dict[str, Any]:
        """Get unsold products"""
        return get_unsold_products_data(
            products_collection, orders_collection, categories_collection, units_collection, taxes_collection,
            store_id, days
        )
    
    @staticmethod
    def get_performance(store_id: str, period: int = 30) -> Dict[str, Any]:
        """Get store performance"""
        return get_store_performance_data(
            sellers_collection, orders_collection, sellerpayouttransactions_collection, store_id, period
        )

class QueryService:
    """Dynamic Query service with AI-powered MongoDB filter generation"""
    
    @staticmethod
    def process_query(request: QueryRequest) -> QueryResponse:
        """Process search query with dynamic MongoDB filter generation and category logic"""
        try:
            session_id = uuid.uuid4().hex[:16]
            user_query = request.query.strip()
            store_obj_id = validate_store_id(request.store_id)
            
            mongo_filter = ai_assistant.generate_mongodb_filter(user_query)
            mongo_filter["seller"] = store_obj_id  
            
            logger.info(f"Using MongoDB filter for '{user_query}': {mongo_filter}")
            products = list(products_collection.find(mongo_filter).limit(50))
            for product in products:
                convert_objectids_to_strings(product)
            category_ids = set()
            for product in products:
                if product.get("category"):
                    try:
                        category_ids.add(ObjectId(product["category"]))
                    except:
                        continue
            categories = []
            for category_id in category_ids:
                try:
                    category = categories_collection.find_one({"_id": category_id})
                    if category:
                        convert_objectids_to_strings(category)
                        categories.append(category)
                except Exception as e:
                    logger.warning(f"Failed to fetch category {category_id}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(products)} products and {len(categories)} categories for query: '{user_query}'")
            ai_response = ai_assistant.get_dynamic_nlp_response(user_query, request.store_id, products, categories)
            if redis_client:
                try:
                    redis_key = f"nlp_session:{session_id}"
                    redis_value = json.dumps({
                        "session_id": session_id,
                        "store_id": request.store_id,
                        "query": user_query,
                        "response": ai_response,
                        "results_count": len(products) + len(categories),
                        "products_found": len(products),
                        "categories_found": len(categories),
                        "mongo_filter_used": mongo_filter,
                        "timestamp": datetime.now().isoformat(),
                        "model_used": "gpt-4o-mini"
                    })
                    redis_client.set(redis_key, redis_value, ex=86400)
                    logger.info(f"Saved enhanced session {session_id} to Redis for store {request.store_id}")
                    
                except Exception as e:
                    logger.warning(f"Failed to save to Redis: {str(e)}")
            
            return QueryResponse(
                session_id=session_id,
                store_id=request.store_id,
                query=user_query,
                response=ai_response
            )
            
        except Exception as e:
            logger.exception("Dynamic query processing failed")
            raise
    
    @staticmethod
    def get_redis_sessions(store_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get stored Redis sessions with optional store filtering"""
        try:
            if not redis_client:
                return {"error": "Redis not available", "sessions": []}
            pattern = "nlp_session:*"
            session_keys = redis_client.keys(pattern)
            
            sessions = []
            for key in session_keys:
                try:
                    session_data = redis_client.get(key)
                    if session_data:
                        session_obj = json.loads(session_data)
                        if store_id and session_obj.get("store_id") != store_id:
                            continue
                        ttl = redis_client.ttl(key)
                        session_obj["ttl_seconds"] = ttl
                        session_obj["expires_in"] = f"{ttl // 3600}h {(ttl % 3600) // 60}m" if ttl > 0 else "expired"
                        
                        sessions.append(session_obj)
                        
                        if len(sessions) >= limit:
                            break
                            
                except Exception as e:
                    logger.warning(f"Failed to parse session {key}: {str(e)}")
                    continue
            sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return {
                "sessions": sessions,
                "total_found": len(sessions),
                "store_filter": store_id,
                "redis_available": True
            }
            
        except Exception as e:
            logger.exception("Failed to get Redis sessions")
            return {"error": str(e), "sessions": []}
    
    @staticmethod
    def get_session_by_id(session_id: str) -> Dict[str, Any]:
        """Get specific session by session ID"""
        try:
            if not redis_client:
                return {"error": "Redis not available"}
            
            redis_key = f"nlp_session:{session_id}"
            session_data = redis_client.get(redis_key)
            
            if not session_data:
                return {"error": "Session not found", "session_id": session_id}
            
            session_obj = json.loads(session_data)
            ttl = redis_client.ttl(redis_key)
            session_obj["ttl_seconds"] = ttl
            session_obj["expires_in"] = f"{ttl // 3600}h {(ttl % 3600) // 60}m" if ttl > 0 else "expired"
            
            return session_obj
            
        except Exception as e:
            logger.exception("Failed to get session")
            return {"error": str(e)}

class AIService:
    """AI service using dynamic queries"""
    
    @staticmethod
    def get_product_substitutes(store_id: str, product_id: str, top_n: int = 5) -> Dict[str, Any]:
        """Get product substitutes using GPT-4o mini"""
        try:
            from bson import ObjectId
            
            store_obj_id = validate_store_id(store_id)
            product_obj_id = ObjectId(product_id)
            original = products_collection.find_one({
                "_id": product_obj_id,
                "seller": store_obj_id
            })
            
            if not original:
                raise Exception("Product not found")
            similar_query = {
                "seller": store_obj_id,
                "status": "APPROVED",
                "_id": {"$ne": product_obj_id}
            }
            
            if original.get("category"):
                similar_query["category"] = original["category"]
            
            similar_products = list(products_collection.find(similar_query).limit(15))
            for product in similar_products:
                convert_objectids_to_strings(product)
                if product.get("category"):
                    try:
                        cat_info = categories_collection.find_one({"_id": ObjectId(product["category"])})
                        product["category"] = cat_info.get("name", "Unknown") if cat_info else "Unknown"
                    except:
                        product["category"] = "Unknown"
            substitutes = ai_assistant.suggest_substitutes(original, similar_products, top_n)
            
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
    
    @staticmethod
    def get_discount_recommendations(store_id: str) -> Dict[str, Any]:
        """Get discount recommendations using GPT"""
        try:
            performance = AnalyticsService.get_performance(store_id, 30)
            unsold_data = AnalyticsService.get_unsold_products(store_id, 30)
            recommendations = ai_assistant.recommend_discounts(
                performance, unsold_data["unsold_products"]
            )
            
            return {
                "store_id": store_id,
                "recommendations": recommendations,
                "ai_model": "gpt-4o-mini",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception("Failed to get discount recommendations")
            raise

