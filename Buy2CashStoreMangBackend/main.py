import logging
import time
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import router
from app.core import Buy2CashException

#logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Buy2Cash Store Management API",
    version="1.0.0",
    description="Store Analytics with AI and Redis Session Tracking"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url} - Client: {request.client.host}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.exception_handler(Buy2CashException)
async def handle_business_error(request: Request, exc: Buy2CashException):
    logger.error(f"Business error: {exc.detail} - URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": "BusinessError",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail} - URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": "HTTPError",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} - URL: {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "type": "ValidationError",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def handle_system_error(request: Request, exc: Exception):
    logger.exception(f"System error: {str(exc)} - URL: {request.url}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "type": "SystemError",
            "path": str(request.url.path)
        }
    )

app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check with system status"""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "features": ["redis_sessions", "gpt4o_mini", "Chat"]
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Buy2Cash API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Buy2Cash API shutting down")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Buy2Cash API on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
