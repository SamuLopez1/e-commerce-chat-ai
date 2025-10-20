import asyncio
from datetime import datetime
from typing import List, Optional

from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.domain.entities import Product, ChatMessage
from src.domain.repositories import IProductRepository, IChatRepository


# ─────────────── Repos Fakes ───────────────

class FakeProductRepo(IProductRepository):
    def __init__(self):
        self._data = [
            Product(id=1, name="Pegasus", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=5),
            Product(id=2, name="Ultraboost", brand="Adidas", category="Running", size="42", color="Blanco", price=150.0, stock=0),
        ]

    def get_all(self) -> List[Product]: return list(self._data)
    def get_by_id(self, product_id: int) -> Optional[Product]:
        return next((p for p in self._data if p.id == product_id), None)
    def get_by_brand(self, brand: str) -> List[Product]:
        return [p for p in self._data if p.brand == brand]
    def get_by_category(self, category: str) -> List[Product]:
        return [p for p in self._data if p.category == category]
    def save(self, product: Product) -> Product:
        if product.id is None:
            product.id = max(p.id for p in self._data) + 1
            self._data.append(product)
        else:
            for i, p in enumerate(self._data):
                if p.id == product.id:
                    self._data[i] = product
                    break
        return product
    def delete(self, product_id: int) -> bool:
        before = len(self._data)
        self._data = [p for p in self._data if p.id != product_id]
        return len(self._data) < before


class FakeChatRepo(IChatRepository):
    def __init__(self):
        self._msgs: list[ChatMessage] = []

    def save_message(self, message: ChatMessage) -> ChatMessage:
        message.id = (max([m.id for m in self._msgs if m.id] + [0]) + 1)
        self._msgs.append(message)
        return message

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        items = [m for m in self._msgs if m.session_id == session_id]
        return items if limit is None else items[-limit:]

    def delete_session_history(self, session_id: str) -> int:
        before = len(self._msgs)
        self._msgs = [m for m in self._msgs if m.session_id != session_id]
        return before - len(self._msgs)

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        items = [m for m in self._msgs if m.session_id == session_id]
        return items[-count:]


class FakeAIService:
    async def generate_response(self, user_message: str, products, context: str) -> str:
        return f"Eco IA: {user_message} (productos={len(products)}, ctx_len={len(context)})"


# ─────────────── Tests ───────────────

def test_product_service_basic_flow():
    svc = ProductService(FakeProductRepo())

    # listar
    allp = svc.get_all_products()
    assert len(allp) == 2

    # crear
    dto = ProductDTO(name="VaporFly", brand="Nike", category="Running", size="42",
                     color="Azul", price=200.0, stock=3, description="Ligera")
    created = svc.create_product(dto)
    assert created.id == 3

    # disponibles
    avail = svc.get_available_products()
    assert all(p.stock > 0 for p in avail)

def test_chat_service_process_message_event_loop():
    product_repo = FakeProductRepo()
    chat_repo = FakeChatRepo()
    ai = FakeAIService()
    svc = ChatService(product_repo, chat_repo, ai)

    req = ChatMessageRequestDTO(session_id="s1", message="Hola, ¿Nike para correr?")
    res = asyncio.run(svc.process_message(req))

    assert res.session_id == "s1"
    assert "Eco IA:" in res.assistant_message