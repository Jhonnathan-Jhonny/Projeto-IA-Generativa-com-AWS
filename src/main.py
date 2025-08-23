from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend import hr_index, hr_rag_response

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/")
async def query_endpoint(request: QuestionRequest):
    try:
        index = hr_index()  # pode futuramente usar cache/global
        response = hr_rag_response(index, request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
