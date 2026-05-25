from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

# Resolve the backend directory dynamically to ensure .env is found regardless of where python is executed
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    OLLAMA_API_KEY: str | None = None
    OLLAMA_MODEL: str = "gemma4:31b-cloud"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Generation defaults
    OLLAMA_TEMPERATURE: float = 0.0
    OLLAMA_TOP_K: int = 40
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_NUM_CTX: int = 2048

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()