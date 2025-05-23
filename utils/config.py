from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    database_url: str
    sync_engine: str

    class Config:
        env_file = ".env"

settings = Settings()