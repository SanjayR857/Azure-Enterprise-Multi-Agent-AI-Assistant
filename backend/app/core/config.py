from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path
import os 
from pydantic import AnyHttpUrl, computed_field
# Resolve the backend directory dynamically to ensure .env is found regardless of where python is executed
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):

    # Azure App Registerations
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000', 'http://localhost:3000']
    TENANT_ID: str = os.getenv("TENANT_ID")
    APP_CLIENT_ID: str = os.getenv("APP_CLIENT_ID")
    OPENAPI_CLIENT_ID: str = os.getenv("OPENAPI_CLIENT_ID")
    SCOPE_DESCRIPTION: str = "access_as_user"

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        return f'api://{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}'

    @computed_field
    @property
    def SCOPES(self) -> dict:
        return {
            self.SCOPE_NAME: self.SCOPE_DESCRIPTION,
        }

    @computed_field
    @property
    def OPENAPI_AUTHORIZATION_URL(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/authorize"

    @computed_field
    @property
    def OPENAPI_TOKEN_URL(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/token"

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

    # LLM Provider Toggle (ollama or azure)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "azure")

    # AZURE OPENAI ENDPOINTS
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL")
    AZURE_OPENAI_MAX_TOKENS: int = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "1000"))
    AZURE_OPENAI_TEMPERATURE: float = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.0"))

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

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()