from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import uuid
from app.core.config import settings
from app.core.database import get_db, init_db
from app.models.models import User
from app.schemas.schemas import (
    UserResponse, CategoryCreate, CategoryResponse, ProductCreate, ProductUpdate, ProductResponse,
    OrderResponse, OrderUpdate, DeliveryZoneCreate, DeliveryZoneResponse
)
from app.services.services import (
    UserService, CategoryService, ProductService, OrderService, DeliveryZoneService
)


app = FastAPI(title="Coffee Shop API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs(settings.media_root, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_root), name="media")


@app.on_event("startup")
async def startup_event():
    await init_db()


# Dependency to check admin
async def get_current_admin(db: AsyncSession = Depends(get_db)) -> User:
    # This is a simplified version - in production use proper auth
    return None  # Implement proper admin authentication


# Category endpoints
@app.post("/api/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    return await service.create(category)


@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    service = CategoryService(db)
    return await service.get_all(active_only)


@app.get("/api/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await service.delete(category)
    return {"message": "Category deleted"}


# Product endpoints
@app.post("/api/products", response_model=ProductResponse)
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    category_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "category_id": category_id
    }
    
    # Handle image upload
    if image:
        file_extension = image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.media_root, file_name)
        
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        product_data["image_url"] = f"/media/{file_name}"
    
    # Handle video upload
    if video:
        file_extension = video.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.media_root, file_name)
        
        with open(file_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        product_data["video_url"] = f"/media/{file_name}"
    
    return await service.create(product_data)


@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = None,
    available_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    if category_id:
        return await service.get_by_category(category_id, available_only)
    return await service.get_all(available_only)


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await service.update(product, product_data)


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await service.delete(product)
    return {"message": "Product deleted"}


# Order endpoints
@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    service = OrderService(db)
    return await service.get_all_orders(limit)


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    order = await service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    from app.models.models import OrderStatus
    service = OrderService(db)
    order = await service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order_data.status:
        status_map = {
            "pending": OrderStatus.PENDING,
            "confirmed": OrderStatus.CONFIRMED,
            "preparing": OrderStatus.PREPARING,
            "ready": OrderStatus.READY,
            "delivering": OrderStatus.DELIVERING,
            "completed": OrderStatus.COMPLETED,
            "cancelled": OrderStatus.CANCELLED
        }
        await service.update_status(order, status_map[order_data.status.value])
    
    return order


# Delivery Zone endpoints
@app.post("/api/delivery-zones", response_model=DeliveryZoneResponse)
async def create_delivery_zone(
    zone: DeliveryZoneCreate,
    db: AsyncSession = Depends(get_db)
):
    service = DeliveryZoneService(db)
    return await service.create(zone)


@app.get("/api/delivery-zones", response_model=List[DeliveryZoneResponse])
async def get_delivery_zones(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    service = DeliveryZoneService(db)
    return await service.get_all(active_only)


@app.delete("/api/delivery-zones/{zone_id}")
async def delete_delivery_zone(zone_id: int, db: AsyncSession = Depends(get_db)):
    service = DeliveryZoneService(db)
    zones = await service.get_all(active_only=False)
    zone = next((z for z in zones if z.id == zone_id), None)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    await service.delete(zone)
    return {"message": "Zone deleted"}


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
