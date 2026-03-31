import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Get variables with hardcoded fallbacks to ensure no 'None' values
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "directory_db")

# URL-encode password (e.g., '@' becomes '%40')
safe_password = urllib.parse.quote_plus(DB_PASS) if DB_PASS else ""

# THE FIX: Ensure this string does NOT contain the word 'driver'
# It must be exactly 'postgresql+psycopg'
DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Debug: This will print the URL to your terminal so you can see if it's malformed
print(f"DEBUG: Attempting to connect with: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()