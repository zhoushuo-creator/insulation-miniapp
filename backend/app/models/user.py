from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime

from app.db.base import Base


class User(Base):
    """微信小程序用户"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    openid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True, comment="微信openid")
    unionid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, comment="微信unionid")
    nickname: Mapped[Optional[str]] = mapped_column(String(100), comment="微信昵称")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), comment="头像URL")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="手机号")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否是后台管理员")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")

    def __repr__(self):
        return f"<User(id={self.id}, openid='{self.openid}', admin={self.is_admin})>"
