from pathlib import Path
from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings

# Load .env files if present
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "ops" / ".env")


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    @model_validator(mode="after")
    def _ensure_postgres(self) -> "Settings":
        if self.APP_ENV != "test" and not self.DATABASE_URL.startswith("postgresql"):
            raise RuntimeError(
                "PostgreSQL required; run inside docker-compose"
            )
        return self


settings = Settings()
