from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ===== Address =====

class AddressCreate(BaseModel):
    name: str
    phone: str
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail: Optional[str] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail: Optional[str] = None
    is_default: Optional[bool] = None


class AddressRead(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Order Item =====

class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    unit_price: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ===== Order =====

class OrderCreateItem(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = 1
    unit_price: float = 0


class OrderCreate(BaseModel):
    items: List[OrderCreateItem]
    address_id: Optional[int] = None
    remark: Optional[str] = None


class OrderRead(BaseModel):
    id: int
    order_no: str
    user_id: int
    address_id: Optional[int] = None
    total_amount: float
    status: str
    remark: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: List[OrderRead]
    total: int
    page: int
    page_size: int
