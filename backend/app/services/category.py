from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.models.category import ProductCategory, ApplicationScenario
from app.models.product import Product
from app.schemas.product import (
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryRead,
    ApplicationScenarioCreate, ApplicationScenarioUpdate, ApplicationScenarioRead,
    ProductRead, ProductListResponse,
)


def _category_to_read(cat: ProductCategory) -> ProductCategoryRead:
    """Convert ORM object to Pydantic schema without children (tree built separately)."""
    return ProductCategoryRead(
        id=cat.id, name=cat.name, name_en=cat.name_en,
        parent_id=cat.parent_id, sort_order=cat.sort_order,
        icon=cat.icon, description=cat.description, is_active=cat.is_active,
    )


def category_to_read(cat: ProductCategory) -> ProductCategoryRead:
    """Public helper: convert a single category without children."""
    return _category_to_read(cat)


def _build_tree(categories: List[ProductCategory], parent_id: Optional[int] = None) -> List[ProductCategoryRead]:
    """Recursively build category tree."""
    result = []
    for cat in categories:
        if cat.parent_id == parent_id:
            node = _category_to_read(cat)
            node.children = _build_tree(categories, cat.id)
            result.append(node)
    result.sort(key=lambda x: x.sort_order)
    return result


async def get_category_tree(db: AsyncSession) -> List[ProductCategoryRead]:
    """Get full category tree."""
    result = await db.execute(
        select(ProductCategory)
        .options(selectinload(ProductCategory.children))
        .order_by(ProductCategory.sort_order)
    )
    categories = result.unique().scalars().all()
    return _build_tree(list(categories))


async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[ProductCategory]:
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id))
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, data: ProductCategoryCreate) -> ProductCategory:
    category = ProductCategory(**data.model_dump())
    db.add(category)
    await db.flush()
    return category


async def update_category(db: AsyncSession, category_id: int, data: ProductCategoryUpdate) -> Optional[ProductCategory]:
    category = await get_category_by_id(db, category_id)
    if not category:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    await db.flush()
    return category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    """Delete a category and reassign subcategories to parent. Returns True if deleted."""
    category = await get_category_by_id(db, category_id)
    if not category:
        return False

    # Reassign children to this category's parent
    parent_id = category.parent_id
    await db.execute(
        update(ProductCategory)
        .where(ProductCategory.parent_id == category_id)
        .values(parent_id=parent_id)
    )

    # Reassign products in this category to parent, or first available sibling
    if parent_id:
        await db.execute(
            update(Product)
            .where(Product.category_id == category_id)
            .values(category_id=parent_id)
        )
    else:
        # Root category: find another root to move products to
        alt = await db.execute(
            select(ProductCategory.id)
            .where(ProductCategory.parent_id == None, ProductCategory.id != category_id)
            .limit(1)
        )
        alt_id = alt.scalar_one_or_none()
        if alt_id:
            await db.execute(
                update(Product).where(Product.category_id == category_id).values(category_id=alt_id)
            )

    await db.delete(category)
    await db.flush()
    return True


async def get_category_products(
    db: AsyncSession,
    category_id: int,
    page: int = 1,
    page_size: int = 20,
) -> ProductListResponse:
    """Get products under a category (including descendants)."""
    # Collect category + all descendants
    result = await db.execute(select(ProductCategory))
    all_cats = result.scalars().all()

    def collect_ids(cat_id: int, cats: List[ProductCategory]) -> List[int]:
        ids = [cat_id]
        for c in cats:
            if c.parent_id == cat_id:
                ids.extend(collect_ids(c.id, cats))
        return ids

    cat_ids = collect_ids(category_id, list(all_cats))

    from sqlalchemy.orm import selectinload

    query = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.scenarios),
        selectinload(Product.variants),
    ).where(
        and_(
            Product.category_id.in_(cat_ids),
            Product.is_published == True,
        )
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Product.is_recommended.desc(), Product.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.unique().scalars().all()

    return ProductListResponse(
        items=[ProductRead.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


# ===== Application Scenarios =====

async def list_scenarios(db: AsyncSession) -> List[ApplicationScenario]:
    result = await db.execute(
        select(ApplicationScenario).order_by(ApplicationScenario.sort_order)
    )
    return result.scalars().all()


async def create_scenario(db: AsyncSession, data: ApplicationScenarioCreate) -> ApplicationScenario:
    scenario = ApplicationScenario(**data.model_dump())
    db.add(scenario)
    await db.flush()
    return scenario


async def update_scenario(db: AsyncSession, scenario_id: int, data: ApplicationScenarioUpdate) -> Optional[ApplicationScenario]:
    result = await db.execute(select(ApplicationScenario).where(ApplicationScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(scenario, key, value)
    await db.flush()
    return scenario


async def delete_scenario(db: AsyncSession, scenario_id: int) -> bool:
    result = await db.execute(select(ApplicationScenario).where(ApplicationScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        return False
    await db.delete(scenario)
    await db.flush()
    return True


async def get_category_count(db: AsyncSession) -> int:
    """Get total category count."""
    result = await db.execute(select(func.count()).select_from(select(ProductCategory.id).subquery()))
    return result.scalar() or 0
