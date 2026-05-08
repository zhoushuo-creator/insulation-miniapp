from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints import products, categories, ai_chat, orders, auth, upload
from app.db.database import get_db
from app.services.product import get_product_count
from app.services.category import get_category_count
from app.services.order import get_order_count
from app.models.chat import ChatSession
from sqlalchemy import select, func as sa_func

api_v1_router = APIRouter()

api_v1_router.include_router(products.router, prefix="/products", tags=["产品"])
api_v1_router.include_router(categories.router, prefix="/categories", tags=["分类"])
api_v1_router.include_router(categories.scenario_router, prefix="/scenarios", tags=["应用场景"])
api_v1_router.include_router(ai_chat.router, prefix="/ai", tags=["AI助手"])
api_v1_router.include_router(orders.router, prefix="/orders", tags=["订单"])
api_v1_router.include_router(orders.address_router, prefix="/addresses", tags=["收货地址"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_v1_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])


@api_v1_router.get("/dashboard", tags=["数据概览"])
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """管理后台仪表盘统计数据"""
    product_count = await get_product_count(db)
    category_count = await get_category_count(db)
    order_count = await get_order_count(db)
    chat_result = await db.execute(select(sa_func.count()).select_from(select(ChatSession.id).subquery()))
    chat_count = chat_result.scalar() or 0
    return {
        "product_count": product_count,
        "category_count": category_count,
        "order_count": order_count,
        "catalog_count": 0,
        "today_chat_count": chat_count,
    }
