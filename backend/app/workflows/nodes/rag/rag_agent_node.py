from langchain_core.messages import content
from langchain_core.messages import AIMessage

from app.rag.retriever import retrieve_documents
# pyrefly: ignore [missing-import]
from app.services.agent_service import agent_service


def rag_agent_node(state):

    question = state["messages"][-1].content

    docs = retrieve_documents(question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""You are a helpful assistant. Answer the latest user question using the provided context.

    Context:
    {context}

    Latest User Question:
    {question}
    """

    response = agent_service.run_chat(prompt)

    return {
        "rag_result": response
    }