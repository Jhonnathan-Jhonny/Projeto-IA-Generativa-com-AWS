from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend import hr_index, hr_rag_response
import asyncio

app = FastAPI()

# Cache global do índice
index_cache = None

class QuestionRequest(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    """Carrega o índice durante a inicialização do app"""
    global index_cache
    print("⏳ Carregando índice vetorial na inicialização...")
    index_cache = hr_index()
    print("✅ Índice vetorial carregado e pronto")

@app.post("/")
async def query_endpoint(request: QuestionRequest):
    try:
        if index_cache is None:
            raise HTTPException(status_code=503, detail="Serviço não está pronto")
        
        response = hr_rag_response(index_cache, request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))