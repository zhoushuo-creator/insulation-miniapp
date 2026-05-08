from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.models.product import Product, ProductVariant
from app.models.category import ProductCategory, ApplicationScenario, product_scenario
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductRead, ProductListResponse,
    ProductVariantCreate, ProductVariantRead,
)


def _build_product_search_text(product: Product) -> str:
    """Aggregate searchable text from product fields for full-text indexing."""
    parts = [product.name]
    if product.model:
        parts.append(product.model)
    if product.brand:
        parts.append(product.brand)
    if product.description:
        parts.append(product.description)
    if product.keywords:
        parts.append(product.keywords)
    if product.specs:
        for v in product.specs.values():
            if isinstance(v, str):
                parts.append(v)
    return " ".join(parts)


async def list_products_with_filter(
    db: AsyncSession,
    *,
    category_id: Optional[int] = None,
    scenario_id: Optional[int] = None,
    keyword: Optional[str] = None,
    thickness_min: Optional[float] = None,
    thickness_max: Optional[float] = None,
    density_min: Optional[float] = None,
    density_max: Optional[float] = None,
    fire_rating: Optional[str] = None,
    min_temp: Optional[float] = None,
    max_temp: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    is_published: Optional[bool] = None,
) -> ProductListResponse:
    """List products with multi-dimensional filtering and pagination."""

    # Base query with joined relationships
    query = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.scenarios),
        selectinload(Product.variants),
    )

    # Filters
    conditions = []

    if is_published is not None:
        conditions.append(Product.is_published == is_published)

    if category_id:
        # Include subcategories
        sub_ids = [category_id]
        result = await db.execute(
            select(ProductCategory.id).where(ProductCategory.parent_id == category_id)
        )
        sub_ids.extend(r[0] for r in result.all())
        conditions.append(Product.category_id.in_(sub_ids))

    if scenario_id:
        query = query.join(
            product_scenario, Product.id == product_scenario.c.product_id
        ).where(product_scenario.c.scenario_id == scenario_id)

    if keyword:
        ilike = f"%{keyword}%"
        conditions.append(
            or_(
                Product.name.ilike(ilike),
                Product.description.ilike(ilike),
                Product.keywords.ilike(ilike),
                Product.model.ilike(ilike),
                Product.brand.ilike(ilike),
                Product.search_text.ilike(ilike),
            )
        )

    # For variant-level filtering (thickness, density), we need subquery approach
    if thickness_min is not None or thickness_max is not None:
        variant_subq = select(ProductVariant.product_id).distinct()
        v_conds = []
        if thickness_min is not None:
            v_conds.append(ProductVariant.thickness >= thickness_min)
        if thickness_max is not None:
            v_conds.append(ProductVariant.thickness <= thickness_max)
        variant_subq = variant_subq.where(and_(*v_conds))
        conditions.append(Product.id.in_(variant_subq))

    if density_min is not None or density_max is not None:
        variant_subq = select(ProductVariant.product_id).distinct()
        v_conds = []
        if density_min is not None:
            v_conds.append(ProductVariant.density >= density_min)
        if density_max is not None:
            v_conds.append(ProductVariant.density <= density_max)
        variant_subq = variant_subq.where(and_(*v_conds))
        conditions.append(Product.id.in_(variant_subq))

    # Fire rating stored in specs JSONB
    if fire_rating:
        conditions.append(Product.specs["fire_rating"].as_string() == fire_rating)

    if min_temp is not None:
        conditions.append(Product.specs["min_temp"].as_string().cast(float) >= min_temp)

    if max_temp is not None:
        conditions.append(Product.specs["max_temp"].as_string().cast(float) <= max_temp)

    if conditions:
        query = query.where(and_(*conditions))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Sort: supports colon suffix _asc / _desc (e.g. reference_price_asc)
    if sort_by.endswith("_asc"):
        sort_col = getattr(Product, sort_by[:-4], None)
        if sort_col:
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(Product.created_at.desc())
    elif sort_by.endswith("_desc"):
        sort_col = getattr(Product, sort_by[:-5], None)
        if sort_col:
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(Product.created_at.desc())
    else:
        sort_col = getattr(Product, sort_by, Product.created_at)
        query = query.order_by(sort_col.desc())

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    products = result.unique().scalars().all()

    return ProductListResponse(
        items=[ProductRead.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_product_detail(db: AsyncSession, product_id: int) -> Optional[Product]:
    """Get product with all relationships loaded."""
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.scenarios),
            selectinload(Product.variants),
        )
        .where(Product.id == product_id)
    )
    return result.unique().scalar_one_or_none()


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    """Create a product with optional variants and scenario links."""
    # Build search text
    search_text_parts = [data.name]
    if data.model:
        search_text_parts.append(data.model)
    if data.brand:
        search_text_parts.append(data.brand)
    if data.description:
        search_text_parts.append(data.description)
    if data.keywords:
        search_text_parts.append(data.keywords)
    if data.specs:
        for v in data.specs.values():
            if isinstance(v, str):
                search_text_parts.append(v)

    product = Product(
        category_id=data.category_id,
        name=data.name,
        model=data.model,
        brand=data.brand,
        description=data.description,
        detail_content=data.detail_content,
        specs=data.specs,
        unit=data.unit,
        reference_price=data.reference_price,
        stock=data.stock,
        cover_image=data.cover_image,
        images=data.images,
        keywords=data.keywords,
        search_text=" ".join(search_text_parts),
        is_published=data.is_published,
        is_recommended=data.is_recommended,
    )

    db.add(product)
    await db.flush()  # get product.id

    # Add variants
    if data.variants:
        for v_data in data.variants:
            variant = ProductVariant(
                product_id=product.id,
                sku=v_data.sku,
                name=v_data.name,
                thickness=v_data.thickness,
                width=v_data.width,
                length=v_data.length,
                density=v_data.density,
                price=v_data.price,
                stock=v_data.stock,
                is_active=v_data.is_active,
            )
            db.add(variant)

    # Link scenarios
    if data.scenario_ids:
        for sid in data.scenario_ids:
            await db.execute(
                product_scenario.insert().values(
                    product_id=product.id, scenario_id=sid
                )
            )

    await db.flush()
    return await get_product_detail(db, product.id)


async def update_product(db: AsyncSession, product_id: int, data: ProductUpdate) -> Optional[Product]:
    """Update a product. Supports partial updates."""
    product = await get_product_detail(db, product_id)
    if not product:
        return None

    update_data = data.model_dump(exclude_unset=True, exclude={"variants", "scenario_ids"})

    # Rebuild search text if fields affecting search are updated
    if any(k in update_data for k in ("name", "model", "brand", "description", "keywords", "specs")):
        search_parts = [
            update_data.get("name", product.name),
            update_data.get("model", product.model or ""),
            update_data.get("brand", product.brand or ""),
            update_data.get("description", product.description or ""),
            update_data.get("keywords", product.keywords or ""),
        ]
        specs = update_data.get("specs", product.specs)
        if specs:
            for v in specs.values():
                if isinstance(v, str):
                    search_parts.append(v)
        update_data["search_text"] = " ".join(p for p in search_parts if p)

    for key, value in update_data.items():
        setattr(product, key, value)

    # Update variants: replace strategy
    if data.variants is not None:
        await db.execute(
            delete(ProductVariant).where(ProductVariant.product_id == product_id)
        )
        for v_data in data.variants:
            variant = ProductVariant(
                product_id=product_id,
                sku=v_data.sku,
                name=v_data.name,
                thickness=v_data.thickness,
                width=v_data.width,
                length=v_data.length,
                density=v_data.density,
                price=v_data.price,
                stock=v_data.stock,
                is_active=v_data.is_active,
            )
            db.add(variant)

    # Update scenarios
    if data.scenario_ids is not None:
        await db.execute(
            delete(product_scenario).where(product_scenario.c.product_id == product_id)
        )
        for sid in data.scenario_ids:
            await db.execute(
                product_scenario.insert().values(product_id=product_id, scenario_id=sid)
            )

    await db.flush()
    return await get_product_detail(db, product_id)


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Delete a product. Returns True if found and deleted."""
    product = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product.scalar_one_or_none()
    if not product:
        return False
    await db.delete(product)
    await db.flush()
    return True


async def get_recommended_products(db: AsyncSession, limit: int = 10) -> List[Product]:
    """Get recommended/published products."""
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.scenarios),
            selectinload(Product.variants),
        )
        .where(
            and_(
                Product.is_published == True,
                Product.is_recommended == True,
            )
        )
        .order_by(Product.updated_at.desc())
        .limit(limit)
    )
    return result.unique().scalars().all()


async def get_product_count(db: AsyncSession) -> int:
    """Get total product count."""
    result = await db.execute(select(func.count()).select_from(select(Product.id).subquery()))
    return result.scalar() or 0
