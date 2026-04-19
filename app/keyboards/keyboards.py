from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Optional
from app.schemas.schemas import CategoryResponse, ProductResponse, OrderItemInCart, DeliveryTypeEnum


class BotKeyboards:
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="☕ Меню")
        builder.button(text="🛒 Корзина")
        builder.button(text="📦 Мои заказы")
        builder.button(text="👤 Профиль")
        builder.adjust(2, 2)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def categories(categories: List[CategoryResponse]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.button(
                text=f"{category.name}",
                callback_data=f"category_{category.id}"
            )
        builder.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def products(products: List[ProductResponse], category_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for product in products:
            builder.button(
                text=f"{product.name} - {product.price:.2f}₽",
                callback_data=f"product_{product.id}"
            )
        builder.button(text="⬅️ Назад к категориям", callback_data=f"categories_{category_id}")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def product_detail(product: ProductResponse, quantity: int = 1) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        # Quantity controls
        builder.button(text="➖", callback_data=f"qty_dec_{product.id}_{quantity}")
        builder.button(text=f"{quantity} шт", callback_data=f"qty_show_{product.id}")
        builder.button(text="➕", callback_data=f"qty_inc_{product.id}_{quantity}")
        
        # Add to cart
        builder.button(
            text=f"🛒 В корзину ({product.price * quantity:.2f}₽)",
            callback_data=f"add_to_cart_{product.id}_{quantity}"
        )
        
        # Back button
        builder.button(text="⬅️ Назад", callback_data=f"back_to_products_{product.category_id}")
        
        builder.adjust(3, 1, 1)
        return builder.as_markup()

    @staticmethod
    def cart(cart_items: List[OrderItemInCart], delivery_type: DeliveryTypeEnum) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        if cart_items:
            # Delivery type selection
            pickup_text = "✅ Самовывоз" if delivery_type == DeliveryTypeEnum.PICKUP else "🏠 Самовывоз"
            delivery_text = "✅ Доставка" if delivery_type == DeliveryTypeEnum.DELIVERY else "🚚 Доставка"
            
            builder.button(text=pickup_text, callback_data="set_pickup")
            builder.button(text=delivery_text, callback_data="set_delivery")
            
            # Checkout button
            builder.button(text="✅ Оформить заказ", callback_data="checkout")
            
            # Clear cart
            builder.button(text="🗑 Очистить корзину", callback_data="clear_cart")
        
        builder.button(text="⬅️ Продолжить покупки", callback_data="back_to_menu")
        builder.adjust(2, 1, 1)
        return builder.as_markup()

    @staticmethod
    def checkout(delivery_type: DeliveryTypeEnum) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        if delivery_type == DeliveryTypeEnum.DELIVERY:
            builder.button(text="📍 Указать адрес доставки", callback_data="set_address")
        
        builder.button(text="📞 Поделиться контактом", request_contact=True)
        builder.button(text="✅ Подтвердить заказ", callback_data="confirm_order")
        builder.button(text="⬅️ Назад", callback_data="back_to_cart")
        
        builder.adjust(1, 1, 1)
        return builder.as_markup()

    @staticmethod
    def order_status(order_id: int, status: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        if status in ["pending", "confirmed"]:
            builder.button(text="❌ Отменить заказ", callback_data=f"cancel_order_{order_id}")
        
        builder.button(text="📦 Мои заказы", callback_data="my_orders")
        builder.button(text="⬅️ В меню", callback_data="back_to_menu")
        
        builder.adjust(1, 1)
        return builder.as_markup()

    @staticmethod
    def my_orders(orders: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for order in orders[:5]:  # Show last 5 orders
            status_emoji = {
                "pending": "⏳",
                "confirmed": "✅",
                "preparing": "👨‍🍳",
                "ready": "🎉",
                "delivering": "🚚",
                "completed": "⭐",
                "cancelled": "❌"
            }.get(order.status, "📦")
            
            builder.button(
                text=f"{status_emoji} Заказ #{order.id} - {order.total_amount:.2f}₽",
                callback_data=f"order_detail_{order.id}"
            )
        
        builder.button(text="⬅️ В меню", callback_data="back_to_menu")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def admin_main() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="📊 Статистика")
        builder.button(text="📦 Заказы")
        builder.button(text="☕ Товары")
        builder.button(text="📂 Категории")
        builder.button(text="🚚 Зоны доставки")
        builder.button(text="👥 Пользователи")
        builder.adjust(2, 2, 2)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def admin_orders(orders: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for order in orders[:10]:
            status_emoji = {
                "pending": "⏳",
                "confirmed": "✅",
                "preparing": "👨‍🍳",
                "ready": "🎉",
                "delivering": "🚚",
                "completed": "⭐",
                "cancelled": "❌"
            }.get(order.status, "📦")
            
            builder.button(
                text=f"{status_emoji} #{order.id} ({order.delivery_type.value})",
                callback_data=f"admin_order_{order.id}"
            )
        
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def admin_order_detail(order_id: int, status: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        status_flow = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["preparing", "cancelled"],
            "preparing": ["ready"],
            "ready": ["delivering"],
            "delivering": ["completed"],
        }
        
        next_statuses = status_flow.get(status, [])
        
        for next_status in next_statuses:
            status_texts = {
                "confirmed": "✅ Подтвердить",
                "preparing": "👨‍🍳 Готовится",
                "ready": "🎉 Готов",
                "delivering": "🚚 Доставляется",
                "completed": "⭐ Завершить",
                "cancelled": "❌ Отменить"
            }
            builder.button(
                text=status_texts.get(next_status, next_status),
                callback_data=f"set_status_{order_id}_{next_status}"
            )
        
        builder.button(text="⬅️ Назад к заказам", callback_data="admin_orders")
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def phone_request() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="📞 Поделиться номером", request_contact=True)
        builder.button(text="⌨️ Ввести вручную")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ В меню", callback_data="back_to_menu")
        return builder.as_markup()
