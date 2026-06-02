from langchain_core.messages import content
from langchain_core.messages import AIMessage

from app.rag.retriever import retrieve_documents
from app.services.llm_service import llm_service


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

    response = llm_service.chat(prompt)

    return {
        "rag_result": response
    }