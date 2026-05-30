from app.rag.vectorstore import vectorstore

def retrieve_documents(query: str):

    docs = vectorstore.similarity_search(
        query,
        k=4
    )

    return docs