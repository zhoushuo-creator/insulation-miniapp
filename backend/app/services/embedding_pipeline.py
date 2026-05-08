"""
产品向量嵌入管线 — 为产品生成 pgvector 向量
"""
from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.embedding import ProductEmbedding
from app.services.embedding import create_embeddings


def _build_product_text(p: Product) -> str:
    """Build rich text representation of a product for embedding."""
    parts = [p.name]
    if p.brand:
        parts.append(f"品牌{p.brand}")
    if p.model:
        parts.append(f"型号{p.model}")
    if p.description:
        parts.append(p.description)
    if p.specs:
        for k, v in p.specs.items():
            if v is not None:
                parts.append(f"{k}:{v}")
    return " ".join(parts)


async def generate_product_embeddings(db: AsyncSession, product_ids: List[int] = None) -> int:
    """
    Generate embeddings for products (by ID list, or all published without embeddings).
    Returns number of products embedded.
    """
    # Find products needing embeddings
    if product_ids:
        stmt = select(Product).where(Product.id.in_(product_ids))
    else:
        # All published products without an existing embedding
        stmt = (
            select(Product)
            .outerjoin(ProductEmbedding, ProductEmbedding.product_id == Product.id)
            .where(
                Product.is_published == True,
                ProductEmbedding.id == None,
            )
        )

    result = await db.execute(stmt.options(selectinload(Product.embeddings)))
    products = result.unique().scalars().all()

    if not products:
        return 0

    texts = [_build_product_text(p) for p in products]
    embeddings = await create_embeddings(texts)

    if not embeddings:
        return 0

    count = 0
    for product, emb in zip(products, embeddings):
        # Delete old embeddings for this product
        await db.execute(
            delete(ProductEmbedding).where(ProductEmbedding.product_id == product.id)
        )
        pe = ProductEmbedding(
            product_id=product.id,
            embedding=emb,
            source_text=_build_product_text(product),
            source_type="product_composite",
            model_name="text-embedding-v3",
        )
        db.add(pe)
        count += 1

    await db.flush()
    return count
