from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from Auth import router as auth_router
from database import engine, Base
from Auth.models import User, OTP

# Initialize FastAPI app
app = FastAPI(
    title="Payvry Payment Platform",
    description="A secure P2P payment platform",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="Frontend/static"), name="static")

# Include routers
app.include_router(
    auth_router.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "API is running"}

@app.get("/auth", response_class=HTMLResponse)
async def auth_page():
    return FileResponse("Frontend/templates/auth.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return FileResponse("Frontend/templates/dashboard.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
