from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vectorstore import vectorstore


class Ingest:

    def ingest_document(self,file_path:str):

        loader = PyPDFLoader(file_path)

        documents = loader.load()

        text_spliter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
        )

        chunks = text_spliter.split_documents(documents)

        vectorstore.add_documents(chunks)

        return len(chunks)