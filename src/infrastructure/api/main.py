"""
Aplicación FastAPI con endpoints:
- GET /, /health
- GET /products, GET /products/{id}
- POST /chat, GET/DELETE /chat/history/{session_id}
"""

from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_session as get_db, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.domain.exceptions import ProductNotFoundError, ChatServiceError

app = FastAPI(title="E-commerce Chat AI", description="API de e-commerce con chat (Gemini)", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.on_event("startup")
def on_startup(): init_db()

@app.get("/")
def root_info():
    return {"name":"E-commerce Chat AI","version":"1.0.0","docs":"/docs",
            "endpoints":["/products","/products/{id}","/chat","/chat/history/{session_id}","/health"],
            "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health(): return {"status":"ok","timestamp":datetime.utcnow().isoformat()}

@app.get("/products", response_model=List[ProductDTO])
def list_products(db: Session = Depends(get_db)):
    svc = ProductService(SQLProductRepository(db))
    return [ProductDTO.model_validate(p) for p in svc.get_all_products()]

@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product(product_id: int, db: Session = Depends(get_db)):
    svc = ProductService(SQLProductRepository(db))
    try:
        return ProductDTO.model_validate(svc.get_product_by_id(product_id))
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    svc = ChatService(SQLProductRepository(db), SQLChatRepository(db), GeminiService())
    try:
        return await svc.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def chat_history(session_id: str, limit: int = 10, db: Session = Depends(get_db)):
    repo = SQLChatRepository(db)
    return [ChatHistoryDTO.model_validate(m) for m in repo.get_session_history(session_id, limit)]

@app.delete("/chat/history/{session_id}")
def delete_history(session_id: str, db: Session = Depends(get_db)):
    repo = SQLChatRepository(db)
    return {"deleted": repo.delete_session_history(session_id)}