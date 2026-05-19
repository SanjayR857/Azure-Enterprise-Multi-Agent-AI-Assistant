from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()
        

class Settings(BaseSettings):
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()