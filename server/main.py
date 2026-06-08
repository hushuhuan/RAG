from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.graph import run_rag, get_available_models
from rag.retriever import retriever

app = FastAPI(title="RAG LangGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    model: str = None  # 可选模型参数
    api_key: str = None  # 可选 API Key 参数

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/api/rag/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        allowed_extensions = [".pdf", ".txt", ".md"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, TXT, MD files are allowed.")
        
        content = await file.read()
        
        if file_ext == ".pdf":
            from rag.loader import load_pdf
            text = load_pdf(content)
        else:
            text = content.decode("utf-8")
        
        await retriever.add_documents([text], file.filename)
        
        return {"message": "File uploaded and processed successfully", "fileName": file.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        result = await run_rag(request.question, request.model, request.api_key)
        
        return {"answer": result["answer"], "sources": result["sources"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/stats")
async def get_stats():
    try:
        stats = await retriever.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/models")
async def get_models():
    """获取可用的大模型列表"""
    return {"models": get_available_models()}

@app.delete("/api/rag/clear")
async def clear_documents():
    try:
        await retriever.clear()
        return {"message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    await retriever.initialize()
    print("Vector store initialized")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5174))
    uvicorn.run(app, host="0.0.0.0", port=port)
