import logging

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
# pyrefly: ignore [missing-import]
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureAgentService:
    """
    Service class responsible for coordinating and running AI tasks.

    This service initializes the language model (LLM) and provides
    a simple chat interface using either Azure OpenAI or Ollama.
    """

    def __init__(self):
        """
        Initializes the AgentService with the configured LLM provider.
        """
        if settings.LLM_PROVIDER.lower() == "azure":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self.model = ChatOpenAI(
                model=settings.AZURE_OPENAI_MODEL,
                base_url=settings.AZURE_OPENAI_ENDPOINT,
                api_key=token_provider,
            )
            logger.info(f"AgentService initialized with Azure OpenAI model: {settings.AZURE_OPENAI_MODEL}")
        else:
            self.model = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0)
            logger.info(f"AgentService initialized with Ollama model: {settings.OLLAMA_MODEL}")

    def run_chat(self, prompt: str) -> str:
        """
        Simple chat function that uses the LLM to generate a response.
        """
        logger.info(f"Running chat with prompt length: {len(prompt)}")
        try:
            result = self.model.invoke(prompt)
            logger.info("Successfully generated chat response")
            return result.content
        except Exception as e:
            logger.error(f"Failed to generate chat response: {e}")
            raise e

azure_agent_service = AzureAgentService()