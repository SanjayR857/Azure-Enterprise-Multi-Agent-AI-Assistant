from langchain_core.messages import content
from langchain_core.messages import AIMessage

from app.rag.retriever import retrieve_documents
from app.services.llm_service import llm_service


def rag_agent_node(state):

    messages = state["messages"]
    question = messages[-1].content

    docs = retrieve_documents(question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Format conversation history
    history_lines = []
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Assistant"
        history_lines.append(f"{role}: {msg.content}")
    conversation_history = "\n".join(history_lines)

    prompt = f"""You are a helpful assistant. Answer the latest user question using the provided context and conversation history.

    Context:
    {context}

    Recent Conversation History:
    {conversation_history}

    Latest User Question:
    {question}
    """

    response = llm_service.chat(prompt)

    return {
        "messages": [
            AIMessage(content=response)
        ]
    }