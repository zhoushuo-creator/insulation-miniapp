"""订单 & 收货地址服务"""
import uuid
from typing import Optional, List
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, Address
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderRead, OrderListResponse,
    AddressCreate, AddressUpdate, AddressRead,
    OrderItemRead,
)


def _generate_order_no() -> str:
    return uuid.uuid4().hex[:16].upper()


async def _get_or_create_dev_user(db: AsyncSession) -> int:
    """Get or create a dev user (for testing without auth)."""
    result = await db.execute(select(User).where(User.openid == "dev-user").limit(1))
    user = result.scalar_one_or_none()
    if not user:
        user = User(openid="dev-user", nickname="开发者", is_admin=True)
        db.add(user)
        await db.flush()
    return user.id


# ===== Orders =====

async def create_order(db: AsyncSession, data: OrderCreate, user_id: Optional[int] = None) -> Order:
    """Create an order from cart items."""
    if not user_id:
        user_id = await _get_or_create_dev_user(db)

    # Calculate total
    total = sum(item.quantity * item.unit_price for item in data.items)

    order = Order(
        order_no=_generate_order_no(),
        user_id=user_id,
        address_id=data.address_id,
        total_amount=total,
        status="pending",
        remark=data.remark,
    )
    db.add(order)
    await db.flush()

    for item_data in data.items:
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            variant_id=item_data.variant_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        db.add(item)

    await db.flush()
    return order


async def get_order_detail(db: AsyncSession, order_id: int) -> Optional[Order]:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    return result.unique().scalar_one_or_none()


async def list_orders(
    db: AsyncSession,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> OrderListResponse:
    query = select(Order).options(selectinload(Order.items))
    if status:
        query = query.where(Order.status == status)

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.unique().scalars().all()

    return OrderListResponse(
        items=[OrderRead.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Optional[Order]:
    """Update order status. Valid transitions: pending→paid→shipped→completed / →cancelled."""
    order = await get_order_detail(db, order_id)
    if not order:
        return None
    order.status = status
    if status == "paid":
        from datetime import datetime, timezone
        order.paid_at = datetime.now(timezone.utc)
    await db.flush()
    return order


async def cancel_order(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Cancel an order (only pending orders can be cancelled)."""
    order = await get_order_detail(db, order_id)
    if not order:
        return None
    if order.status != "pending":
        return None
    order.status = "cancelled"
    await db.flush()
    return order


# ===== Addresses =====

async def create_address(db: AsyncSession, data: AddressCreate, user_id: Optional[int] = None) -> Address:
    if not user_id:
        user_id = await _get_or_create_dev_user(db)

    if data.is_default:
        await db.execute(
            update(Address).where(Address.user_id == user_id).values(is_default=False)
        )

    addr = Address(
        name=data.name,
        phone=data.phone,
        province=data.province or "",
        city=data.city or "",
        district=data.district or "",
        detail=data.detail or "",
        is_default=data.is_default,
        user_id=user_id,
    )
    db.add(addr)
    await db.flush()
    return addr


async def list_addresses(db: AsyncSession, user_id: Optional[int] = None) -> List[Address]:
    if not user_id:
        user_id = await _get_or_create_dev_user(db)
    result = await db.execute(
        select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    return result.scalars().all()


async def update_address(db: AsyncSession, address_id: int, data: AddressUpdate) -> Optional[Address]:
    result = await db.execute(select(Address).where(Address.id == address_id))
    addr = result.scalar_one_or_none()
    if not addr:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(addr, key, value)

    if update_data.get("is_default"):
        await db.execute(
            update(Address).where(Address.user_id == addr.user_id, Address.id != addr.id).values(is_default=False)
        )

    await db.flush()
    return addr


async def delete_address(db: AsyncSession, address_id: int) -> bool:
    result = await db.execute(select(Address).where(Address.id == address_id))
    addr = result.scalar_one_or_none()
    if not addr:
        return False
    await db.delete(addr)
    await db.flush()
    return True


async def get_order_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(select(Order.id).subquery()))
    return result.scalar() or 0
