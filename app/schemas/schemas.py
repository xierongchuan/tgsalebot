from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryTypeEnum(str, Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


# User Schemas
class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sort_order: int = 0


class ProductCreate(ProductBase):
    category_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    category_id: int
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# OrderItem Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price: float

    class Config:
        from_attributes = True


# Order Schemas
class OrderItemInCart(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    image_url: Optional[str] = None


class Cart(BaseModel):
    items: List[OrderItemInCart] = []
    delivery_type: DeliveryTypeEnum = DeliveryTypeEnum.PICKUP
    delivery_address: Optional[str] = None
    comment: Optional[str] = None

    def total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)


class OrderCreate(BaseModel):
    delivery_type: DeliveryTypeEnum
    delivery_address: Optional[str] = None
    comment: Optional[str] = None
    items: List[OrderItemInCart]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    delivery_address: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatusEnum
    delivery_type: DeliveryTypeEnum
    delivery_address: Optional[str] = None
    total_amount: float
    comment: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


# DeliveryZone Schemas
class DeliveryZoneBase(BaseModel):
    name: str
    min_order_amount: float = 0.0
    delivery_fee: float = 0.0


class DeliveryZoneCreate(DeliveryZoneBase):
    pass


class DeliveryZoneResponse(DeliveryZoneBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
