from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.schemas.order import (
    OrderCreate, OrderRead, OrderListResponse,
    AddressCreate, AddressUpdate, AddressRead,
)
from app.services.order import (
    create_order, get_order_detail, list_orders,
    update_order_status, cancel_order,
    create_address, list_addresses, update_address, delete_address,
)

router = APIRouter()
address_router = APIRouter()


# ===== 订单 =====

@router.post("")
async def create_order_endpoint(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建订单"""
    order = await create_order(db, data)
    return OrderRead.model_validate(await get_order_detail(db, order.id))


@router.get("")
async def list_orders_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """订单列表"""
    return await list_orders(db, status=status, page=page, page_size=page_size)


@router.get("/{order_id}")
async def get_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """订单详情"""
    order = await get_order_detail(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return OrderRead.model_validate(order)


@router.put("/{order_id}/status")
async def update_status(
    order_id: int,
    status: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """更新订单状态（管理端）"""
    order = await update_order_status(db, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"message": f"订单状态已更新为 {status}"}


@router.put("/{order_id}/cancel")
async def cancel_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """取消订单"""
    order = await cancel_order(db, order_id)
    if not order:
        raise HTTPException(status_code=400, detail="订单不存在或不可取消")
    return {"message": "订单已取消"}


# ===== 收货地址 =====

@address_router.get("")
async def list_addresses_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """收货地址列表"""
    addrs = await list_addresses(db)
    return {"items": [AddressRead.model_validate(a) for a in addrs]}


@address_router.post("")
async def create_address_endpoint(
    data: AddressCreate,
    db: AsyncSession = Depends(get_db),
):
    """新增收货地址"""
    addr = await create_address(db, data)
    return AddressRead.model_validate(addr)


@address_router.put("/{address_id}")
async def update_address_endpoint(
    address_id: int,
    data: AddressUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新收货地址"""
    addr = await update_address(db, address_id, data)
    if not addr:
        raise HTTPException(status_code=404, detail="地址不存在")
    return AddressRead.model_validate(addr)


@address_router.delete("/{address_id}")
async def delete_address_endpoint(
    address_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除收货地址"""
    deleted = await delete_address(db, address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="地址不存在")
    return {"message": "删除成功"}
