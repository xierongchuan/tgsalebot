from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.keyboards.keyboards import BotKeyboards
from app.services.services import UserService, OrderService
from sqlalchemy.ext.asyncio import AsyncSession


def create_admin_handlers(dp: Router, session_factory, admin_username: str):
    
    @dp.message(F.text == "📊 Статистика")
    async def show_stats(message: types.Message, session: AsyncSession):
        # Check if user is admin
        if not await is_admin(message, session, admin_username):
            await message.answer("❌ Доступ запрещен")
            return
        
        order_service = OrderService(session)
        orders = await order_service.get_all_orders(limit=1000)
        
        total_orders = len(orders)
        pending_orders = sum(1 for o in orders if o.status.value == "pending")
        completed_orders = sum(1 for o in orders if o.status.value == "completed")
        total_revenue = sum(o.total_amount for o in orders if o.status.value == "completed")
        
        stats_text = f"<b>📊 Статистика</b>\n\n"
        stats_text += f"Всего заказов: {total_orders}\n"
        stats_text += f"Ожидают: {pending_orders}\n"
        stats_text += f"Завершены: {completed_orders}\n"
        stats_text += f"💰 Выручка: {total_revenue:.2f}₽\n"
        
        await message.answer(stats_text, reply_markup=BotKeyboards.admin_main())

    @dp.message(F.text == "📦 Заказы")
    async def show_admin_orders(message: types.Message, session: AsyncSession):
        if not await is_admin(message, session, admin_username):
            await message.answer("❌ Доступ запрещен")
            return
        
        order_service = OrderService(session)
        orders = await order_service.get_all_orders(limit=20)
        
        if not orders:
            await message.answer("Нет активных заказов", reply_markup=BotKeyboards.admin_main())
            return
        
        await message.answer(
            "<b>Последние заказы:</b>",
            reply_markup=BotKeyboards.admin_orders(orders)
        )

    @dp.callback_query(F.data.startswith("admin_order_"))
    async def show_admin_order_detail(callback: types.CallbackQuery, session: AsyncSession):
        order_id = int(callback.data.split("_")[2])
        
        order_service = OrderService(session)
        order = await order_service.get_by_id(order_id)
        
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        status_texts = {
            "pending": "⏳ Ожидает подтверждения",
            "confirmed": "✅ Подтвержден",
            "preparing": "👨‍🍳 Готовится",
            "ready": "🎉 Готов к выдаче/доставке",
            "delivering": "🚚 Доставляется",
            "completed": "⭐ Завершен",
            "cancelled": "❌ Отменен"
        }
        
        order_text = f"<b>Заказ #{order.id}</b>\n\n"
        order_text += f"Статус: {status_texts.get(order.status.value, '📦')}\n"
        order_text += f"Клиент: {order.user.first_name or ''} {order.user.last_name or ''}\n"
        order_text += f"Телефон: {order.user.phone or 'Не указан'}\n"
        order_text += f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        order_text += f"Тип: {'Доставка' if order.delivery_type.value == 'delivery' else 'Самовывоз'}\n"
        if order.delivery_address:
            order_text += f"Адрес: {order.delivery_address}\n"
        if order.comment:
            order_text += f"Комментарий: {order.comment}\n"
        order_text += f"\n<b>Товары:</b>\n"
        for item in order.items:
            order_text += f"• {item.product.name} x{item.quantity} - {item.price * item.quantity:.2f}₽\n"
        order_text += f"\n💰 Итого: {order.total_amount:.2f}₽"
        
        await callback.message.edit_text(
            order_text,
            reply_markup=BotKeyboards.admin_order_detail(order.id, order.status.value)
        )

    @dp.callback_query(F.data.startswith("set_status_"))
    async def set_order_status(callback: types.CallbackQuery, session: AsyncSession):
        data = callback.data.split("_")
        order_id = int(data[2])
        new_status = data[3]
        
        order_service = OrderService(session)
        order = await order_service.get_by_id(order_id)
        
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        from app.models.models import OrderStatus
        status_map = {
            "confirmed": OrderStatus.CONFIRMED,
            "preparing": OrderStatus.PREPARING,
            "ready": OrderStatus.READY,
            "delivering": OrderStatus.DELIVERING,
            "completed": OrderStatus.COMPLETED,
            "cancelled": OrderStatus.CANCELLED
        }
        
        await order_service.update_status(order, status_map[new_status])
        
        # Notify user
        try:
            await callback.bot.send_message(
                chat_id=int(order.user.telegram_id),
                text=f"📦 Статус заказа #{order.id} изменен на: {status_texts.get(new_status, new_status)}"
            )
        except:
            pass
        
        await show_admin_order_detail(callback, session)

    @dp.callback_query(F.data == "admin_orders")
    async def back_to_admin_orders(callback: types.CallbackQuery, session: AsyncSession):
        order_service = OrderService(session)
        orders = await order_service.get_all_orders(limit=20)
        
        await callback.message.edit_text(
            "<b>Последние заказы:</b>",
            reply_markup=BotKeyboards.admin_orders(orders)
        )

    async def is_admin(message: types.Message, session: AsyncSession, admin_username: str) -> bool:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user:
            return False
        
        # Check by username or is_admin flag
        return user.is_admin or (user.username and user.username.lower() == admin_username.lower())
