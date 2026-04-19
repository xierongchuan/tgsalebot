from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional
from app.models.models import User, Category, Product, Order, OrderItem, OrderStatus, DeliveryType, DeliveryZone
from app.schemas.schemas import UserCreate, CategoryCreate, ProductCreate, ProductUpdate, OrderCreate, DeliveryZoneCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_phone(self, user: User, phone: str) -> User:
        user.phone = phone
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_address(self, user: User, address: str) -> User:
        user.address = address
        await self.db.commit()
        await self.db.refresh(user)
        return user


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, active_only: bool = True) -> List[Category]:
        query = select(Category)
        if active_only:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, category_data: CategoryCreate) -> Category:
        category = Category(**category_data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category: Category, **kwargs) -> Category:
        for key, value in kwargs.items():
            setattr(category, key, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_category(self, category_id: int, available_only: bool = True) -> List[Product]:
        query = select(Product).where(Product.category_id == category_id)
        if available_only:
            query = query.where(Product.is_available == True)
        query = query.order_by(Product.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_all(self, available_only: bool = True) -> List[Product]:
        query = select(Product)
        if available_only:
            query = query.where(Product.is_available == True)
        query = query.order_by(Product.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, product_data: dict) -> Product:
        product = Product(**product_data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product, product_data: ProductUpdate) -> Product:
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, order_data: OrderCreate, user_id: int) -> Order:
        total_amount = sum(item.price * item.quantity for item in order_data.items)
        
        order = Order(
            user_id=user_id,
            delivery_type=order_data.delivery_type,
            delivery_address=order_data.delivery_address,
            comment=order_data.comment,
            total_amount=total_amount
        )
        
        self.db.add(order)
        await self.db.flush()
        
        for item in order_data.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price
            )
            self.db.add(order_item)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: int) -> List[Order]:
        result = await self.db.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_orders(self, limit: int = 50) -> List[Order]:
        result = await self.db.execute(
            select(Order).order_by(Order.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, order: Order) -> Order:
        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(order)
        return order


class DeliveryZoneService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, active_only: bool = True) -> List[DeliveryZone]:
        query = select(DeliveryZone)
        if active_only:
            query = query.where(DeliveryZone.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, zone_data: DeliveryZoneCreate) -> DeliveryZone:
        zone = DeliveryZone(**zone_data.model_dump())
        self.db.add(zone)
        await self.db.commit()
        await self.db.refresh(zone)
        return zone

    async def delete(self, zone: DeliveryZone) -> None:
        await self.db.delete(zone)
        await self.db.commit()
