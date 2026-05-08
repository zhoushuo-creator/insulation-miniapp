from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.deps import require_admin
from app.schemas.product import (
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryRead,
    ApplicationScenarioCreate, ApplicationScenarioUpdate, ApplicationScenarioRead,
)
from app.services.category import (
    get_category_tree,
    get_category_by_id,
    category_to_read,
    create_category,
    update_category,
    delete_category,
    get_category_products,
    list_scenarios,
    create_scenario,
    update_scenario,
    delete_scenario,
)

router = APIRouter()
scenario_router = APIRouter()


# ===== 产品分类 =====

@router.get("")
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """获取分类树结构"""
    tree = await get_category_tree(db)
    return {"items": tree}


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取单个分类详情"""
    category = await get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category_to_read(category)


@router.get("/{category_id}/products")
async def category_products(
    category_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取某分类下的产品列表（含子分类）"""
    return await get_category_products(db, category_id, page=page, page_size=page_size)


@router.post("")
async def create_category_endpoint(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """创建分类（管理端）"""
    category = await create_category(db, data)
    return category_to_read(category)


@router.put("/{category_id}")
async def update_category_endpoint(
    category_id: int,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """更新分类（管理端）"""
    category = await update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category_to_read(category)


@router.delete("/{category_id}")
async def delete_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """删除分类（管理端）"""
    deleted = await delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


# ===== 应用场景 =====

@scenario_router.get("")
async def list_scenarios_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """获取所有应用场景标签"""
    scenarios = await list_scenarios(db)
    return {"items": [ApplicationScenarioRead.model_validate(s) for s in scenarios]}


@scenario_router.post("")
async def create_scenario_endpoint(
    data: ApplicationScenarioCreate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """创建应用场景（管理端）"""
    scenario = await create_scenario(db, data)
    return ApplicationScenarioRead.model_validate(scenario)


@scenario_router.put("/{scenario_id}")
async def update_scenario_endpoint(
    scenario_id: int,
    data: ApplicationScenarioUpdate,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """更新应用场景（管理端）"""
    scenario = await update_scenario(db, scenario_id, data)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return ApplicationScenarioRead.model_validate(scenario)


@scenario_router.delete("/{scenario_id}")
async def delete_scenario_endpoint(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    # admin=Depends(require_admin),  # 暂时关闭验证
):
    """删除应用场景（管理端）"""
    deleted = await delete_scenario(db, scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="场景不存在")
    return {"message": "删除成功"}
