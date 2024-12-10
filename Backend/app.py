from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from Auth import router as auth_router
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from webhooks.router import router as webhook_router

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include auth router
app.include_router(
    auth_router.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

# Mount the webhook router
app.include_router(webhook_router)

def check_auth(request: Request) -> bool:
    token = request.cookies.get("access_token")
    return bool(token)

@app.get("/")
def read_root():
    return {"status": "healthy"}

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return FileResponse("Frontend/templates/login.html")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return FileResponse("Frontend/templates/signup.html")

@app.get("/auth")
async def auth_redirect():
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return FileResponse("Frontend/templates/dashboard.html")

@app.get("/register_face", response_class=HTMLResponse)
async def register_face_page(request: Request):
    return FileResponse("frontend/templates/register_face.html")

@app.get("/verify_face", response_class=HTMLResponse)
async def verify_face_page(request: Request):
    return FileResponse("Frontend/templates/verify_face.html")

@app.get("/authorize-transfer")
async def authorize_transfer_page(
    request: Request, 
    amount: str, 
    account_number: str, 
    bank_code: str, 
    bank_name: str, 
    recipient_name: str
):
    return FileResponse("Frontend/templates/authorize.html")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
    