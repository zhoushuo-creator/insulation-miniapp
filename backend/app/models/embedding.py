from sqlalchemy import Integer, String, Text, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from typing import Optional
from datetime import datetime

from app.db.base import Base


class ProductEmbedding(Base):
    """产品向量嵌入（pgvector），用于语义搜索"""
    __tablename__ = "product_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )

    embedding = mapped_column(Vector(1024), nullable=False, comment="1024维向量")

    source_text: Mapped[str] = mapped_column(Text, comment="被向量化的原始文本(用于溯源)")
    source_type: Mapped[str] = mapped_column(
        String(50), comment="来源类型: product_composite / description / specs_json / catalog_page"
    )
    model_name: Mapped[str] = mapped_column(String(100), comment="嵌入模型名称")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")

    product = relationship("Product", back_populates="embeddings")

    __table_args__ = (
        Index(
            "idx_product_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": "100"},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self):
        return f"<ProductEmbedding(id={self.id}, product_id={self.product_id})>"


class DocumentChunk(Base):
    """纸质资料数字化后的文本块 + 向量"""
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_name: Mapped[str] = mapped_column(String(255), comment="原始文件名")
    page_number: Mapped[Optional[int]] = mapped_column(Integer, comment="来源页码")
    chunk_index: Mapped[int] = mapped_column(Integer, comment="文本块序号")

    content: Mapped[str] = mapped_column(Text, nullable=False, comment="文本内容")

    embedding = mapped_column(Vector(1024), nullable=False, comment="1024维向量")

    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, comment="OCR置信度、页面坐标等")

    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")

    __table_args__ = (
        Index(
            "idx_doc_chunk_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": "100"},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc='{self.document_name}', chunk={self.chunk_index})>"
