from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage

class IProductRepository(ABC):
    """
    Contrato de acceso a productos (Dominio).
    Las implementaciones concretas estarán en la capa de infraestructura.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por ID; retorna None si no existe."""
        raise NotImplementedError

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos de una marca específica (Nike, Adidas, etc.)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos de una categoría específica (Running, Casual...)."""
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto.
        Si no tiene ID, crea uno nuevo y retorna la entidad con su ID.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID. Retorna True si existía y fue eliminado."""
        raise NotImplementedError
    
class IChatRepository(ABC):
    """
    Contrato para gestionar el historial de conversaciones (memoria).
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje y retorna el mensaje persistido (con ID si aplica)."""
        raise NotImplementedError

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene el historial de una sesión; si `limit` se define, retorna solo los últimos N
        en **orden cronológico** (más antiguos primero).
        """
        raise NotImplementedError

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina todo el historial de una sesión. Retorna cantidad de mensajes borrados."""
        raise NotImplementedError

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Retorna los últimos `count` mensajes en **orden cronológico**."""
        raise NotImplementedError