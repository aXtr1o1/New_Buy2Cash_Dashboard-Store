import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient


logger = logging.getLogger(__name__)

load_dotenv(".env")


MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client[MONGODB_DB]

products_collection = db["products"]

orders_collection = db["orders"]
logger.info(f"Orders count: {orders_collection.count_documents({})}")
categories_collection = db["categories"]
subcategories_collection = db["subCategories"]
sellers_collection = db["sellers"]
units_collection = db["units"]
taxes_collection = db["taxes"]
sellerpayouttransactions_collection = db["sellerpayouttransactions"]


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
