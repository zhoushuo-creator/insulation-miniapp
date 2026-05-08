from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.deps import get_current_user, require_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead
from app.services.product import (
    list_products_with_filter,
    get_product_detail,
    create_product,
    update_product,
    delete_product,
    get_recommended_products,
)

router = APIRouter()


@router.get("")
async def list_products(
    category_id: int | None = Query(None, description="分类ID (含子分类)"),
    scenario_id: int | None = Query(None, description="应用场景ID"),
    keyword: str | None = Query(None, description="搜索关键词"),
    thickness_min: float | None = Query(None, description="最小厚度mm"),
    thickness_max: float | None = Query(None, description="最大厚度mm"),
    density_min: float | None = Query(None, description="最小密度kg/m³"),
    density_max: float | None = Query(None, description="最大密度kg/m³"),
    fire_rating: str | None = Query(None, description="防火等级: A1/A2/B1"),
    min_temp: float | None = Query(None, description="最低使用温度℃"),
    max_temp: float | None = Query(None, description="最高使用温度℃"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    db: AsyncSession = Depends(get_db),
):
    """产品列表，支持多维度筛选和分页"""
    return await list_products_with_filter(
        db,
        category_id=category_id,
        scenario_id=scenario_id,
        keyword=keyword,
        thickness_min=thickness_min,
        thickness_max=thickness_max,
        density_min=density_min,
        density_max=density_max,
        fire_rating=fire_rating,
        min_temp=min_temp,
        max_temp=max_temp,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        is_published=True,  # public API only shows published
    )


@router.get("/recommended")
async def recommended_products(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """首页推荐产品"""
    products = await get_recommended_products(db, limit=limit)
    return {
        "items": [ProductRead.model_validate(p) for p in products],
        "limit": limit,
    }


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """全文关键词搜索"""
    return await list_products_with_filter(
        db,
        keyword=q,
        page=page,
        page_size=page_size,
        sort_by="created_at",
        is_published=True,
    )


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """产品详情（含变体和场景标签）"""
    product = await get_product_detail(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ProductRead.model_validate(product)


@router.post("")
async def create_product_endpoint(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭认证便于验证
):
    """创建产品（管理端）"""
    product = await create_product(db, data)
    return ProductRead.model_validate(product)


@router.put("/{product_id}")
async def update_product_endpoint(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭
):
    """更新产品（管理端）"""
    product = await update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ProductRead.model_validate(product)


@router.delete("/{product_id}")
async def delete_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭
):
    """删除产品（管理端）"""
    deleted = await delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="产品不存在")
    return {"message": "删除成功"}
