"""
Servicio de aplicación para el chat con IA.
Orquesta repositorios y servicio externo (Gemini) para procesar mensajes.
"""

from datetime import datetime, UTC
from typing import Optional

from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
)
from src.domain.entities import ChatContext, ChatMessage
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
    """
    Casos de uso del chat (Application Layer).

    Constructor:
        - product_repo: IProductRepository
        - chat_repo: IChatRepository
        - ai_service: servicio externo con método async:
              generate_response(user_message: str, products: list, context: str) -> str

    Métodos:
        - process_message(request: ChatMessageRequestDTO) -> ChatMessageResponseDTO
        - get_session_history(session_id, limit) -> list[ChatMessage]
        - clear_session_history(session_id) -> int
    """

    def __init__(self, product_repo: IProductRepository, chat_repo: IChatRepository, ai_service):
        self._product_repo = product_repo
        self._chat_repo = chat_repo
        self._ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Flujo:
          1) Obtener todos los productos
          2) Obtener historial reciente (últimos 6)
          3) Crear ChatContext
          4) Llamar a ai_service.generate_response(...)
          5) Guardar msg usuario
          6) Guardar msg asistente
          7) Retornar ChatMessageResponseDTO
        """
        products = self._product_repo.get_all()

        recent = self._chat_repo.get_recent_messages(session_id=request.session_id, count=6)
        context = ChatContext(messages=recent, max_messages=6).format_for_prompt()

        # Llamada a IA (async)
        assistant_text = await self._ai_service.generate_response(
            user_message=request.message,
            products=products,
            context=context,
        )

        # Guardar mensajes
        now = datetime.now(UTC)
        user_msg = ChatMessage(
            id=None, session_id=request.session_id, role="user",
            message=request.message, timestamp=now
        )
        self._chat_repo.save_message(user_msg)

        assistant_msg = ChatMessage(
            id=None, session_id=request.session_id, role="assistant",
            message=assistant_text, timestamp=datetime.utcnow()
        )
        self._chat_repo.save_message(assistant_msg)

        return ChatMessageResponseDTO(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=assistant_text,
            timestamp=datetime.now(UTC),
        )

    def get_session_history(self, session_id: str, limit: Optional[int] = None):
        """Devuelve el historial de una sesión (orden cronológico)."""
        return self._chat_repo.get_session_history(session_id=session_id, limit=limit)

    def clear_session_history(self, session_id: str) -> int:
        """Elimina el historial de una sesión; retorna cantidad de mensajes borrados."""
        return self._chat_repo.delete_session_history(session_id=session_id)