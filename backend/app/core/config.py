from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path
import os 
# Resolve the backend directory dynamically to ensure .env is found regardless of where python is executed
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):

    # OLLAMA ENDPOINTS 
    OLLAMA_API_KEY: str | None = None
    OLLAMA_MODEL: str = "gemma4:31b-cloud"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # EMBDING MODELS
    OLLAMA_EMBDING_MODEL: str =  os.getenv("OLLAMA_EMBDING_MODEL")


    # Generation defaults
    OLLAMA_TEMPERATURE: float = 0.0
    OLLAMA_TOP_K: int = 40
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_NUM_CTX: int = 2048

    # Postgres DB Config
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    # Web Search
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

    # Langsmith
    LANGSMITH_TRACING: str = "false"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "console")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/app.log")
    LOG_FILE_MAX_BYTES: int = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))
    LOG_FILE_BACKUP_COUNT: int = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()