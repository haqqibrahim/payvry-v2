from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Auth import router as auth_router
from database import engine, Base

# Initialize FastAPI app
app = FastAPI(
    title="Payvry Payment Platform",
    description="A secure P2P payment platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(
    auth_router.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
