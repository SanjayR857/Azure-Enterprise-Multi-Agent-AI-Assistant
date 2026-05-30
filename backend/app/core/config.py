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

    # Web Search
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

    # Langsmith
    LANGSMITH_TRACING: str = "true"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT")

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()