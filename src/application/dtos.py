from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic import ConfigDict


class ProductDTO(BaseModel):
    """DTO para transferir datos de productos."""
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v is None or v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        if v is None or v < 0:
            raise ValueError("El stock no puede ser negativo.")
        return v


class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes del usuario."""
    session_id: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        return v

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío.")
        return v


class ChatMessageResponseDTO(BaseModel):
    """DTO para enviar respuestas del chat."""
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para mostrar historial de chat."""
    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
