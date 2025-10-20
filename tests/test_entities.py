import pytest
from datetime import datetime, timedelta

from src.domain.entities import Product, ChatMessage, ChatContext


# ───────────────── Tests de Product ─────────────────

def test_product_validations_ok():
    p = Product(
        id=None, name="Pegasus", brand="Nike", category="Running",
        size="42", color="Negro", price=120.0, stock=5, description="Zapatilla"
    )
    assert p.name == "Pegasus"
    assert p.price == 120.0
    assert p.stock == 5

def test_product_invalid_name():
    with pytest.raises(ValueError):
        Product(
            id=None, name="  ", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5
        )

def test_product_invalid_price():
    with pytest.raises(ValueError):
        Product(
            id=None, name="Pegasus", brand="Nike", category="Running",
            size="42", color="Negro", price=0, stock=5
        )

def test_product_invalid_stock():
    with pytest.raises(ValueError):
        Product(
            id=None, name="Pegasus", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=-1
        )

def test_product_is_available_and_stock_ops():
    p = Product(
        id=1, name="Pegasus", brand="Nike", category="Running",
        size="42", color="Negro", price=120.0, stock=2
    )
    assert p.is_available() is True
    p.reduce_stock(1)
    assert p.stock == 1
    p.increase_stock(3)
    assert p.stock == 4


# ───────────────── Tests de ChatMessage ─────────────────

def test_chatmessage_validations_ok():
    now = datetime.utcnow()
    m = ChatMessage(id=None, session_id="s1", role="user", message="hola", timestamp=now)
    assert m.role == "user"
    assert m.message == "hola"

def test_chatmessage_invalid_role():
    now = datetime.utcnow()
    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="s1", role="admin", message="hola", timestamp=now)

def test_chatmessage_empty_message():
    now = datetime.utcnow()
    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="s1", role="user", message="   ", timestamp=now)


# ───────────────── Tests de ChatContext ─────────────────

def test_chatcontext_format_for_prompt_keeps_last_n_and_format():
    base = datetime.utcnow() - timedelta(minutes=10)
    msgs = []
    for i in range(8):
        role = "user" if i % 2 == 0 else "assistant"
        msgs.append(ChatMessage(id=i+1, session_id="s", role=role, message=f"m{i+1}", timestamp=base + timedelta(minutes=i)))

    ctx = ChatContext(messages=msgs, max_messages=6)
    text = ctx.format_for_prompt()

    # Debe incluir solo los últimos 6 mensajes: m3..m8
    assert "user: m3" in text
    assert "assistant: m8" in text
    assert "m1" not in text and "m2" not in text
