# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.ingest import Ingest
from app.rag.retriever import retrieve_documents

router = APIRouter(
    prefix="/api/rag",
    tags=["rag"],
)

class IngestRequest(BaseModel):
    file_path: str

class QueryRequest(BaseModel):
    query: str

@router.post("/ingest")
async def ingest_file(request: IngestRequest):
    try:
        ingester = Ingest()
        num_chunks = ingester.ingest_document(request.file_path)
        return {
            "status": "success",
            "message": f"Successfully ingested document. Created {num_chunks} chunks.",
            "chunks_created": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_rag(request: QueryRequest):
    try:
        docs = retrieve_documents(request.query)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
