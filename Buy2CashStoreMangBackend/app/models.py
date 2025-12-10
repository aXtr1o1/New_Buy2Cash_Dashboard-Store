from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class StoreInfo(BaseModel):
    """Enhanced store information"""
    store_id: str
    store_name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payout_balance: float = 0.0
    total_products: int = 0
    recent_orders: int = 0

class StoresResponse(BaseModel):
    """Stores response"""
    stores: List[StoreInfo]

class QueryRequest(BaseModel):
    """Enhanced search query request"""
    store_id: str = Field(..., description="Your store ID")
    query: str = Field(..., min_length=1, max_length=200, description="What are you looking for?")
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Please enter a search query')
        return v.strip()

class QueryResponse(BaseModel):
    """Enhanced search response with Redis session tracking"""
    session_id: str
    store_id: str
    query: str
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class PopularSearch(BaseModel):
    """Simplified popular search item"""
    sno: int
    contextual_category: str
    search_query: str

class PopularSearchesResponse(BaseModel):
    """Popular searches response"""
    popular_searches: List[PopularSearch]

class RedisSession(BaseModel):
    """Redis session data model - Fixed Pydantic v2 warning"""
    session_id: str
    store_id: str
    query: str
    response: str
    results_count: int
    timestamp: str
    model_used: str 
    ttl_seconds: Optional[int] = None
    expires_in: Optional[str] = None
    model_config = {
        "protected_namespaces": (),
    }

class RedisSessionsResponse(BaseModel):
    """Redis sessions response - Fixed Pydantic v2 warning"""
    sessions: List[RedisSession]
    total_found: int
    store_filter: Optional[str] = None
    redis_available: bool
    model_config = {
        "protected_namespaces": (),
    }

class SessionByIdResponse(BaseModel):
    """Single session response"""
    session_id: Optional[str] = None
    store_id: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None
    results_count: Optional[int] = None
    timestamp: Optional[str] = None
    model_used: str = Field(alias="ai_model_name") 
    ttl_seconds: Optional[int] = None
    expires_in: Optional[str] = None
    error: Optional[str] = None
    model_config = {
        "protected_namespaces": (),
    }
