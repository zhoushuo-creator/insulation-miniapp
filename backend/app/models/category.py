from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.db.base import Base

# 产品↔应用场景 多对多关联表
product_scenario = Table(
    "product_scenario",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("scenario_id", Integer, ForeignKey("application_scenarios.id", ondelete="CASCADE"), primary_key=True),
)


class ProductCategory(Base):
    """产品分类，树形结构（parent_id 自关联）"""
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称，如 岩棉板")
    name_en: Mapped[Optional[str]] = mapped_column(String(100), comment="英文名称")
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("product_categories.id"), nullable=True, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序序号")
    icon: Mapped[Optional[str]] = mapped_column(String(255), comment="分类图标URL")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="分类描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 自引用：子分类 / 父分类
    children = relationship("ProductCategory", back_populates="parent", remote_side=[id])
    parent = relationship("ProductCategory", back_populates="children", remote_side=[parent_id])

    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"


class ApplicationScenario(Base):
    """应用场景标签（如：屋顶保温、管道保温、工业窑炉等）"""
    __tablename__ = "application_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="场景名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="场景描述")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    products = relationship("Product", secondary=product_scenario, back_populates="scenarios")

    def __repr__(self):
        return f"<ApplicationScenario(id={self.id}, name='{self.name}')>"
