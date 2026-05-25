from langchain_ollama import ChatOllama


from app.core.config import settings


class LLMService:

    def __init__(self):
        self.model = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0)
    
    
    def chat(self, prompt: str) -> str:
        result = self.model.invoke(prompt)
        return result.content



llm_service = LLMService()
