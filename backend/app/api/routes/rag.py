# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.ingest import Ingest
from app.rag.retriever import retrieve_documents

import logging

logger = logging.getLogger(__name__)

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
    logger.info(f"Received ingest request for file: {request.file_path}")
    try:
        ingester = Ingest()
        num_chunks = ingester.ingest_document(request.file_path)
        logger.info(f"Successfully ingested {request.file_path} into {num_chunks} chunks")
        return {
            "status": "success",
            "message": f"Successfully ingested document. Created {num_chunks} chunks.",
            "chunks_created": num_chunks
        }
    except Exception as e:
        logger.error(f"Failed to ingest document {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_rag(request: QueryRequest):
    logger.info(f"Received RAG query request: '{request.query}'")
    try:
        docs = retrieve_documents(request.query)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        logger.info(f"Successfully retrieved {len(docs)} documents for query")
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to retrieve documents for query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
