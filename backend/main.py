from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from api import router

load_dotenv()

app = FastAPI(title="Buy2Cash API")

# CORS configuration so the Next.js frontend can call this API from the browser

app.add_middleware(
    CORSMiddleware,
     allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes defined in api.py
app.include_router(router)


if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


