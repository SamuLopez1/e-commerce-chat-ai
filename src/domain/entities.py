from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Product: 
    """
    Entidad que representa un producto en el e-commerce.
    Contiene la lógica de negocio relacionada con productos.
    """
    
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""
    
    def __post_init__(self):
        """
        Validaciones que se ejecutan después de crear el objeto.
        TODO: Implementar validaciones:
        - price debe ser mayor a 0
        - stock no puede ser negativo
        - name no puede estar vacío
        Lanza ValueError si alguna validación falla
        """
        
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.price is None or self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        if self.stock is None or self.stock < 0:
            raise ValueError("El stock no puede ser negativo.")
    
    def is_available(self) -> bool:
        """
        TODO: Retorna True si el producto tiene stock disponible
        """
        
        return self.stock > 0
    
    def reduce_stock(self, quantity: int) -> None:
        
        """
        TODO: Reduce el stock del producto
        - Valida que quantity sea positivo
        - Valida que haya suficiente stock
        - Lanza ValueError si no se puede reducir
        """
        if quantity is None or quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva.")
        if quantity > self.stock:
            raise ValueError("No hay stock suficiente para la operación.")
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        
        """
        TODO: Aumenta el stock del producto
        - Valida que quantity sea positivo
        """
        
        if quantity is None or quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva.")
        self.stock += quantity
        
@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en el chat.
    """
    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime
    
    def __post_init__(self):
        """
        TODO: Implementar validaciones:
        - role debe ser 'user' o 'assistant'
        - message no puede estar vacío
        - session_id no puede estar vacío
        """
        
        if self.role not in {"user", "assistant"}:
            raise ValueError("El rol debe ser 'user' o 'assistant'.")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")
    
    def is_from_user(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del usuario
        """
        
        return self.role == "user"
    
    def is_from_assistant(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del asistente
        """
        
        return self.role == "assistant"
    
@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.
    Mantiene los mensajes recientes para dar coherencia al chat.
    """
    messages: list[ChatMessage]
    max_messages: int = 6
    
    def get_recent_messages(self) -> list[ChatMessage]:
        """
        TODO: Retorna los últimos N mensajes (max_messages)
        Pista: Usa slicing de Python messages[-self.max_messages:]
        """
        return self.messages[-self.max_messages :]
    
    def format_for_prompt(self) -> str:
        """
        TODO: Formatea los mensajes para incluirlos en el prompt de IA
        Formato esperado:
        "Usuario: mensaje del usuario
        Asistente: respuesta del asistente
        Usuario: otro mensaje
        ..."
        
        Pista: Itera sobre get_recent_messages() y construye el string
        """
        lines: list[str] = []
        for m in self.get_recent_messages():
            prefix = "Usuario" if m.is_from_user() else "Asistente"
            lines.append(f"{prefix}: {m.message}")
        return "\n".join(lines)