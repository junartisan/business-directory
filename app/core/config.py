import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# Load the .env file from the root directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Philippine Cities Directory"
    
    # These must match your .env keys
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"

    # Social Logins
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    FB_CLIENT_ID: Optional[str] = None
    FB_CLIENT_SECRET: Optional[str] = None
    FB_REDIRECT_URI: Optional[str] = None

    # --- THE FIX IS HERE ---
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # This tells Pydantic: "If you see db_user, just ignore it."
    )

settings = Settings()