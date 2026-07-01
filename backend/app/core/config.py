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
    TENANT_ID: str = os.getenv("TENANT_ID", "")
    APP_CLIENT_ID: str = os.getenv("APP_CLIENT_ID", "")
    OPENAPI_CLIENT_ID: str = os.getenv("OPENAPI_CLIENT_ID", "")
    SCOPE_DESCRIPTION: str = os.getenv("SCOPE_DESCRIPTION", "access_as_user")

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
    OLLAMA_API_KEY: str | None = os.getenv("OLLAMA_API_KEY")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # EMBDING MODELS
    OLLAMA_EMBDING_MODEL: str = os.getenv("OLLAMA_EMBDING_MODEL", "")

    # Generation defaults
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))
    OLLAMA_TOP_K: int = int(os.getenv("OLLAMA_TOP_K", "40"))
    OLLAMA_TOP_P: float = float(os.getenv("OLLAMA_TOP_P", "0.9"))
    OLLAMA_NUM_CTX: int = int(os.getenv("OLLAMA_NUM_CTX", "2048"))

    # LLM Provider Toggle (ollama or azure)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "azure")

    # AZURE OPENAI ENDPOINTS
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", "")
    AZURE_OPENAI_MAX_TOKENS: int = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "1000"))
    AZURE_OPENAI_TEMPERATURE: float = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.0"))

    # Database Provider Toggle (postgres or azure_cosmos)
    DB_PROVIDER: str = os.getenv("DB_PROVIDER", "postgres")

    # Azure Cosmos DB NoSQL Config
    AZURE_COSMOS_ENDPOINT: str = os.getenv("AZURE_COSMOS_ENDPOINT", "")
    AZURE_COSMOS_KEY: str = os.getenv("AZURE_COSMOS_KEY", "")
    AZURE_COSMOS_DATABASE: str = os.getenv("AZURE_COSMOS_DATABASE", "")
    AZURE_COSMOS_CONTAINER: str = os.getenv("AZURE_COSMOS_CONTAINER", "")

    # Web Search
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

    # Langsmith
    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "false")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "console")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() in ("true", "1", "yes")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/app.log")
    LOG_FILE_MAX_BYTES: int = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))
    LOG_FILE_BACKUP_COUNT: int = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))
    
    # Attachments
    ALLOWED_ATTACHMENT_EXTENSIONS: set[str] = {'.pdf', '.png', '.jpg', '.jpeg', '.mp4', '.mov', '.txt', '.csv'}
    ALLOWED_ATTACHMENT_MIME_TYPES: set[str] = {'application/pdf', 'image/png', 'image/jpeg', 'video/mp4', 'video/quicktime', 'text/plain', 'text/csv'}
    MAX_ATTACHMENT_SIZE_MB: int = 10
    STORAGE_ACCOUNT_NAME: str = os.getenv("STORAGE_ACCOUNT_NAME", "")

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()