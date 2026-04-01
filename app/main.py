from fastapi import FastAPI
from app.routers import businesses, auth, search
from app.db.session import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# This name MUST match the "app" in your uvicorn command (app.main:app)
app = FastAPI(title="Philippine Cities Online Directory")

app.include_router(businesses.router)
app.include_router(auth.router, prefix="/auth") # 2. The Registration

app.include_router(search.router)

#app.include_router(auth.router, prefix="/auth")

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"status": "Local Development Server is Live"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This tells FastAPI: "If someone goes to /static, show them files in the 'static' folder"
app.mount("/static", StaticFiles(directory="static"), name="static")