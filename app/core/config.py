from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Bot Configuration
    bot_token: str
    admin_username: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./coffee_shop.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Media
    media_root: str = "/workspace/static/media"
    max_upload_size: int = 10485760  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
