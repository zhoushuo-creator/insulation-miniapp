from sqlalchemy import Integer, String, Float, Boolean, Text, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime

from app.db.base import Base


class Address(Base):
    """收货地址"""
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="收货人姓名")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="联系电话")
    province: Mapped[str] = mapped_column(String(50), comment="省")
    city: Mapped[str] = mapped_column(String(50), comment="市")
    district: Mapped[str] = mapped_column(String(50), comment="区")
    detail: Mapped[str] = mapped_column(String(200), comment="详细地址")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否默认地址")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(server_default="NOW()", onupdate="NOW()")

    def __repr__(self):
        return f"<Address(id={self.id}, name='{self.name}')>"


class Order(Base):
    """订单主表"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, comment="订单编号")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="下单用户"
    )
    address_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("addresses.id"), comment="收货地址"
    )
    total_amount: Mapped[float] = mapped_column(
        DECIMAL(10, 2), default=0.00, comment="订单总金额(元)"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending",
        comment="状态: pending(待付款) / paid(已付款) / shipped(已发货) / completed(已完成) / cancelled(已取消)"
    )
    remark: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="支付时间")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(server_default="NOW()", onupdate="NOW()")

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, no='{self.order_no}', status='{self.status}')>"


class OrderItem(Base):
    """订单行项目"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    variant_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("product_variants.id"), nullable=True, comment="变体ID"
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="数量")
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="下单时单价(元)")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")

    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"
