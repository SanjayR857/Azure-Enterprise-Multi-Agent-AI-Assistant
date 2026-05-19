from langchain_ollama import ChatOllama


from app.core.config import settings


class LLMService:

    def __init__(self):
        self.model = ChatOllama(model=settings.OLLAMA_MODEL, temperature=1, top_k=0.75,top_p=0.9,repeat_last_n=10)
    
    
    def invoke(self, prompt: str) -> str:
        result = self.model.invoke(prompt)
        return result.content



llm_service = LLMService()
