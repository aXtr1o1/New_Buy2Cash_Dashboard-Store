import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
import redis

logger = logging.getLogger(__name__)

load_dotenv("Buy2CashStoreMang/config.env")
# MongoDB Configuration

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client[MONGODB_DB]
# Collections
products_collection = db["products"]

orders_collection = db["orders"]
logger.info(f"Orders count: {orders_collection.count_documents({})}")
categories_collection = db["categories"]
subcategories_collection = db["subCategories"]
sellers_collection = db["sellers"]
units_collection = db["units"]
taxes_collection = db["taxes"]
sellerpayouttransactions_collection = db["sellerpayouttransactions"]

# Supabase configuration 
supabase_client = None
try:
    from supabase import create_client
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase connected")
    else:
        logger.warning("Supabase not configured")
        
except Exception as e:
    logger.warning(f"Supabase connection failed: {str(e)}")

# Redis configuration
# redis_client = None
# try:
#     REDIS_URL = os.getenv("REDIS_URL")
#     redis_client = redis.from_url(REDIS_URL, decode_responses=True)
#     redis_client.ping()
#     logger.info("Redis connected successfully")
    
# except Exception as e:
#     logger.warning(f"Redis connection failed: {str(e)}")
#     redis_client = None
