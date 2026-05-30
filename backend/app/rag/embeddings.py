from langchain_ollama import OllamaEmbeddings

from app.core.config import settings



embeddings = OllamaEmbeddings(
    model=settings.OLLAMA_EMBDING_MODEL
)
