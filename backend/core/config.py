from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ACCESS_COOKIE_NAME: str = "my_acsess_token"
    POSTER_API_KEY: str = os.getenv("OMDB_API_KEY")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()