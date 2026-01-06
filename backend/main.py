from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import router


app = FastAPI(title="Buy2Cash API")

# CORS configuration so the Next.js frontend can call this API from the browser
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


