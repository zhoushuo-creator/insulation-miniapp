from sqlalchemy import Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime

from app.db.base import Base


class ChatSession(Base):
    """AI 对话会话"""
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True, comment="关联用户"
    )
    openid: Mapped[Optional[str]] = mapped_column(String(100), index=True, comment="微信用户 openid")
    title: Mapped[Optional[str]] = mapped_column(String(200), comment="会话标题(自动生成)")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(server_default="NOW()", onupdate="NOW()")

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}')>"


class ChatMessage(Base):
    """AI 对话消息"""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), comment="角色: user / assistant / system")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")

    # RAG 溯源
    sources: Mapped[Optional[list]] = mapped_column(JSON, comment="引用的产品/资料列表")
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), comment="使用的LLM模型")
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, comment="Token消耗")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}')>"
