from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


# ===== Product Category =====

class ProductCategoryCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategoryRead(BaseModel):
    id: int
    name: str
    name_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    children: List["ProductCategoryRead"] = []

    model_config = {"from_attributes": True}

    @field_validator("children", mode="before")
    @classmethod
    def coerce_children(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            return [v] if v else []
        return v


# ===== Application Scenario =====

class ApplicationScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0


class ApplicationScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ApplicationScenarioRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    sort_order: int

    model_config = {"from_attributes": True}


# ===== Product Variant =====

class ProductVariantCreate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    thickness: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    density: Optional[float] = None
    price: Optional[float] = None
    stock: int = 9999
    is_active: bool = True


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    thickness: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    density: Optional[float] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    sku: Optional[str] = None
    name: Optional[str] = None
    thickness: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    density: Optional[float] = None
    price: Optional[float] = None
    stock: int = 9999
    is_active: bool

    model_config = {"from_attributes": True}


# ===== Product =====

class ProductCreate(BaseModel):
    category_id: int
    name: str
    model: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    detail_content: Optional[str] = None
    specs: Optional[dict] = None
    unit: Optional[str] = None
    reference_price: Optional[float] = None
    stock: int = 9999
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    keywords: Optional[str] = None
    is_published: bool = False
    is_recommended: bool = False
    scenario_ids: Optional[List[int]] = None
    variants: Optional[List[ProductVariantCreate]] = None


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    detail_content: Optional[str] = None
    specs: Optional[dict] = None
    unit: Optional[str] = None
    reference_price: Optional[float] = None
    stock: Optional[int] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    keywords: Optional[str] = None
    is_published: Optional[bool] = None
    is_recommended: Optional[bool] = None
    scenario_ids: Optional[List[int]] = None
    variants: Optional[List[ProductVariantCreate]] = None


class ProductRead(BaseModel):
    id: int
    category_id: int
    name: str
    model: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    detail_content: Optional[str] = None
    specs: Optional[dict] = None
    unit: Optional[str] = None
    reference_price: Optional[float] = None
    stock: int
    cover_image: Optional[str] = None
    images: Optional[List[Any]] = None
    keywords: Optional[str] = None
    is_published: bool
    is_recommended: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[ProductCategoryRead] = None
    scenarios: List[ApplicationScenarioRead] = []
    variants: List[ProductVariantRead] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: List[ProductRead]
    total: int
    page: int
    page_size: int
