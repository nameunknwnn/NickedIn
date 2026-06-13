from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    DATABASE_URL:str
    FRONTEND_URL:str
    JWT_SECRET:str
    class Config:
        env_file = ".env"

settings=Settings()