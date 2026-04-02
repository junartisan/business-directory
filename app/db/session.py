import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import the Base we created in the other file to stay consistent
from app.db.base_class import Base 

load_dotenv()

# 1. DATABASE CONFIGURATION
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "directory_db")

# URL-encode password (handles special characters like '@' in passwords)
safe_password = urllib.parse.quote_plus(DB_PASS) if DB_PASS else ""

# Construct the URL
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Debug: Check your terminal to ensure the URL is formed correctly
print(f"DEBUG: Attempting to connect with: {SQLALCHEMY_DATABASE_URL}")

# 2. ENGINE CREATION
# Added pool_pre_ping to prevent the "SSL SYSCALL" timeout error we saw earlier
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

# 3. SESSION & UTILITIES
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """
    Call this in main.py to generate tables on the Postgres server.
    """
    # Important: Ensure your models are imported before calling this
    Base.metadata.create_all(bind=engine)