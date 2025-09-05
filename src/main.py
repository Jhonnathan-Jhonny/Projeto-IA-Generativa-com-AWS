from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.ragResponse import hr_rag_response
from indexing.vectorStore import hr_index
from contextlib import asynccontextmanager 

# Cache global do índice
index_cache = None

class QuestionRequest(BaseModel):
    question: str

@asynccontextmanager
async def startup_event(app: FastAPI):
    #Carrega o índice durante a inicialização do app
    global index_cache
    index_cache = hr_index()
    yield

app = FastAPI(lifespan=startup_event)

@app.post("/")
async def query_endpoint(request: QuestionRequest):
    try:
        if index_cache is None:
            raise HTTPException(status_code=503, detail="Serviço não está pronto")
        
        response = hr_rag_response(index_cache, request.question)
        print(f"Pergunta: {request.question}\nResposta: {response}")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))