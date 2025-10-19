from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .rag_chain import rag_answer

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message is required")
    result = await rag_answer(req.message)
    return result
