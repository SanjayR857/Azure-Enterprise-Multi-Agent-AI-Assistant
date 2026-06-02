from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.utilities import SQLDatabase
from app.services.llm_service import llm_service
from langchain_ollama import ChatOllama
from app.core.config import settings


class SQLAgentService:
    def __init__(self):
        self.db = SQLDatabase.from_uri(
            "sqlite:///app/database/sample.db"
        )

        self.llm = ChatOllama(model=settings.OLLAMA_MODEL, temperature=0)

        self.toolkit = SQLDatabaseToolkit(
            db=self.db,
            llm=self.llm
        )

        self.sql_agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=False,
            handle_parsing_errors=True
        )
        self.sql_agent.handle_parsing_errors = True


sql_agent_service = SQLAgentService()

