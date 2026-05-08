from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import datetime

from app.db.base import Base
from app.models.category import product_scenario


class Product(Base):
    """产品主表"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_categories.id"), nullable=False, index=True,
        comment="所属分类ID"
    )

    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    model: Mapped[Optional[str]] = mapped_column(String(100), comment="型号/编号")
    brand: Mapped[Optional[str]] = mapped_column(String(100), comment="品牌")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="产品描述")
    detail_content: Mapped[Optional[str]] = mapped_column(Text, comment="富文本详情(HTML/Markdown)")

    # 技术参数 — JSONB 灵活存储
    specs: Mapped[Optional[dict]] = mapped_column(JSONB, comment="技术规格参数")

    # 价格与库存
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="计价单位: 立方米/平方米/米/吨")
    reference_price: Mapped[Optional[float]] = mapped_column(Float, comment="参考单价(元)")
    stock: Mapped[int] = mapped_column(Integer, default=9999, comment="库存数量")

    # 媒体
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), comment="封面图URL")
    images: Mapped[Optional[list]] = mapped_column(JSON, comment="图片列表URL数组")

    # 搜索辅助
    keywords: Mapped[Optional[str]] = mapped_column(String(500), comment="SEO关键词，逗号分隔")
    search_text: Mapped[Optional[str]] = mapped_column(Text, comment="聚合搜索文本(用于全文检索)")

    # 状态
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否上架")
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否推荐")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(server_default="NOW()", comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(server_default="NOW()", onupdate="NOW()", comment="更新时间")

    # 关联关系
    category = relationship("ProductCategory", back_populates="products")
    scenarios = relationship("ApplicationScenario", secondary=product_scenario, back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    embeddings = relationship("ProductEmbedding", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_products_category", "category_id"),
        Index("idx_products_published", "is_published"),
        Index("idx_products_search", "search_text", postgresql_using="gin",
              postgresql_ops={"search_text": "gin_trgm_ops"}),
        Index("idx_products_specs", "specs", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class ProductVariant(Base):
    """产品规格变体（如不同厚度、尺寸的 SKU）"""
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[Optional[str]] = mapped_column(String(100), unique=True, comment="SKU编码")
    name: Mapped[Optional[str]] = mapped_column(String(200), comment="变体名称，如 50mm厚岩棉板")

    # 变体规格（可从父产品继承或覆盖）
    thickness: Mapped[Optional[float]] = mapped_column(Float, comment="厚度 mm")
    width: Mapped[Optional[float]] = mapped_column(Float, comment="宽度 mm")
    length: Mapped[Optional[float]] = mapped_column(Float, comment="长度 mm")
    density: Mapped[Optional[float]] = mapped_column(Float, comment="密度 kg/m3")

    price: Mapped[Optional[float]] = mapped_column(Float, comment="变体价格(元)")
    stock: Mapped[Optional[int]] = mapped_column(Integer, default=9999, comment="库存")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")

    product = relationship("Product", back_populates="variants")

    def __repr__(self):
        return f"<ProductVariant(id={self.id}, name='{self.name}')>"
