from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: Optional[str] = None
    PROJECT_VERSION: str

    ENVIRONMENT: str = 'production'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
