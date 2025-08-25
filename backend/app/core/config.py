from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from ops directory if present
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / "ops" / ".env")


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str


settings = Settings()
