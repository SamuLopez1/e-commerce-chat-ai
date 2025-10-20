"""
Repositorio concreto de chat usando SQLAlchemy.
Cumple IChatRepository (guardar y consultar historial).
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel

def _model_to_entity(m: ChatMemoryModel) -> ChatMessage:
    return ChatMessage(id=m.id, session_id=m.session_id, role=m.role,
                       message=m.message, timestamp=m.timestamp)

def _entity_to_model(e: ChatMessage) -> ChatMemoryModel:
    return ChatMemoryModel(id=e.id, session_id=e.session_id, role=e.role,
                           message=e.message, timestamp=e.timestamp)

class SQLChatRepository(IChatRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        orm = _entity_to_model(message)
        self.db.add(orm); self.db.commit(); self.db.refresh(orm)
        message.id = orm.id
        return message

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        q = (self.db.query(ChatMemoryModel)
             .filter(ChatMemoryModel.session_id == session_id)
             .order_by(ChatMemoryModel.timestamp.asc()))
        rows = q.all()
        if limit is not None:
            rows = rows[-limit:]
        return [_model_to_entity(r) for r in rows]

    def delete_session_history(self, session_id: str) -> int:
        rows = (self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id).all())
        n = len(rows)
        for r in rows:
            self.db.delete(r)
        self.db.commit()
        return n

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        q = (self.db.query(ChatMemoryModel)
             .filter(ChatMemoryModel.session_id == session_id)
             .order_by(ChatMemoryModel.timestamp.desc())
             .limit(count))
        rows = list(reversed(q.all()))  # devolver cronológico
        return [_model_to_entity(r) for r in rows]