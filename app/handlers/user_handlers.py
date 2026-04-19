from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.keyboards import BotKeyboards
from app.services.services import UserService, CategoryService, ProductService, OrderService
from app.schemas.schemas import UserCreate, Cart, OrderItemInCart, DeliveryTypeEnum, OrderCreate
from sqlalchemy.ext.asyncio import AsyncSession


class RegistrationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()


class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_comment = State()
    waiting_for_phone_checkout = State()


def create_user_handlers(dp: Router, session_factory):
    
    @dp.message(F.text == "👤 Профиль")
    async def show_profile(message: types.Message, session: AsyncSession):
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user:
            # Register new user
            user_data = UserCreate(
                telegram_id=str(message.from_user.id),
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            user = await user_service.create(user_data)
        
        profile_text = f"👤 <b>Ваш профиль</b>\n\n"
        profile_text += f"Имя: {user.first_name or 'Не указано'}\n"
        profile_text += f"Телефон: {user.phone or 'Не указан'}\n"
        profile_text += f"Адрес: {user.address or 'Не указан'}\n"
        
        await message.answer(profile_text, reply_markup=BotKeyboards.main_menu())

    @dp.message(F.text == "☕ Меню")
    async def show_menu(message: types.Message, session: AsyncSession):
        category_service = CategoryService(session)
        categories = await category_service.get_all()
        
        if not categories:
            await message.answer("Меню временно недоступно", reply_markup=BotKeyboards.main_menu())
            return
        
        menu_text = "<b>☕ Наше меню</b>\n\nВыберите категорию:"
        await message.answer(menu_text, reply_markup=BotKeyboards.categories(categories))

    @dp.callback_query(F.data.startswith("category_"))
    async def show_category_products(callback: types.CallbackQuery, session: AsyncSession):
        category_id = int(callback.data.split("_")[1])
        
        product_service = ProductService(session)
        products = await product_service.get_by_category(category_id)
        
        if not products:
            await callback.answer("В этой категории пока нет товаров", show_alert=True)
            return
        
        await callback.message.edit_text(
            "<b>Выберите товар:</b>",
            reply_markup=BotKeyboards.products(products, category_id)
        )

    @dp.callback_query(F.data.startswith("product_"))
    async def show_product_detail(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
        product_id = int(callback.data.split("_")[1])
        
        product_service = ProductService(session)
        product = await product_service.get_by_id(product_id)
        
        if not product:
            await callback.answer("Товар не найден", show_alert=True)
            return
        
        # Store current quantity in state
        await state.update_data(current_quantity=1, current_product_id=product_id)
        
        product_text = f"<b>{product.name}</b>\n\n"
        if product.description:
            product_text += f"{product.description}\n\n"
        product_text += f"💰 Цена: {product.price:.2f}₽"
        
        await callback.message.edit_text(
            product_text,
            reply_markup=BotKeyboards.product_detail(product, quantity=1)
        )

    @dp.callback_query(F.data.startswith("qty_inc_"))
    async def increase_quantity(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
        data = callback.data.split("_")
        product_id = int(data[2])
        quantity = int(data[3]) + 1
        
        await state.update_data(current_quantity=quantity)
        
        product_service = ProductService(session)
        product = await product_service.get_by_id(product_id)
        
        if product:
            await callback.message.edit_text(
                f"<b>{product.name}</b>\n\n💰 Цена: {product.price:.2f}₽",
                reply_markup=BotKeyboards.product_detail(product, quantity=quantity)
            )

    @dp.callback_query(F.data.startswith("qty_dec_"))
    async def decrease_quantity(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
        data = callback.data.split("_")
        product_id = int(data[2])
        quantity = max(1, int(data[3]) - 1)
        
        await state.update_data(current_quantity=quantity)
        
        product_service = ProductService(session)
        product = await product_service.get_by_id(product_id)
        
        if product:
            await callback.message.edit_text(
                f"<b>{product.name}</b>\n\n💰 Цена: {product.price:.2f}₽",
                reply_markup=BotKeyboards.product_detail(product, quantity=quantity)
            )

    @dp.callback_query(F.data.startswith("add_to_cart_"))
    async def add_to_cart(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
        data = callback.data.split("_")
        product_id = int(data[3])
        quantity = int(data[4])
        
        product_service = ProductService(session)
        product = await product_service.get_by_id(product_id)
        
        if not product:
            await callback.answer("Товар не найден", show_alert=True)
            return
        
        # Get current cart from state
        cart_data = await state.get_value("cart")
        if not cart_data:
            cart = Cart(items=[])
        else:
            cart = Cart(**cart_data)
        
        # Check if product already in cart
        existing_item = next((item for item in cart.items if item.product_id == product_id), None)
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart.items.append(OrderItemInCart(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=quantity,
                image_url=product.image_url
            ))
        
        await state.update_value("cart", cart.model_dump())
        
        await callback.answer(f"✅ {product.name} добавлен в корзину!", show_alert=False)
        
        # Show cart preview
        cart_text = f"<b>🛒 Корзина</b>\n\n"
        for item in cart.items:
            cart_text += f"• {item.product_name} x{item.quantity} - {item.price * item.quantity:.2f}₽\n"
        cart_text += f"\n💰 Итого: {cart.total():.2f}₽"
        
        await callback.message.edit_text(
            cart_text,
            reply_markup=BotKeyboards.cart(cart.items, cart.delivery_type)
        )

    @dp.message(F.text == "🛒 Корзина")
    async def show_cart(message: types.Message, state: FSMContext):
        cart_data = await state.get_value("cart")
        
        if not cart_data or not cart_data.get("items"):
            await message.answer("Ваша корзина пуста ☹️", reply_markup=BotKeyboards.main_menu())
            return
        
        cart = Cart(**cart_data)
        
        cart_text = f"<b>🛒 Ваша корзина</b>\n\n"
        for item in cart.items:
            cart_text += f"• {item.product_name} x{item.quantity} - {item.price * item.quantity:.2f}₽\n"
        cart_text += f"\n💰 Итого: {cart.total():.2f}₽"
        
        await message.answer(cart_text, reply_markup=BotKeyboards.cart(cart.items, cart.delivery_type))

    @dp.callback_query(F.data == "clear_cart")
    async def clear_cart(callback: types.CallbackQuery, state: FSMContext):
        await state.update_value("cart", None)
        await callback.message.edit_text("Корзина очищена 🗑", reply_markup=BotKeyboards.main_menu())

    @dp.callback_query(F.data == "set_pickup")
    async def set_pickup(callback: types.CallbackQuery, state: FSMContext):
        cart_data = await state.get_value("cart")
        if cart_data:
            cart = Cart(**cart_data)
            cart.delivery_type = DeliveryTypeEnum.PICKUP
            cart.delivery_address = None
            await state.update_value("cart", cart.model_dump())
            
            await callback.message.edit_text(
                "✅ Выбран самовывоз",
                reply_markup=BotKeyboards.cart(cart.items, cart.delivery_type)
            )

    @dp.callback_query(F.data == "set_delivery")
    async def set_delivery(callback: types.CallbackQuery, state: FSMContext):
        cart_data = await state.get_value("cart")
        if cart_data:
            cart = Cart(**cart_data)
            cart.delivery_type = DeliveryTypeEnum.DELIVERY
            await state.update_value("cart", cart.model_dump())
            
            await callback.message.edit_text(
                "🚚 Выбрана доставка",
                reply_markup=BotKeyboards.cart(cart.items, cart.delivery_type)
            )

    @dp.callback_query(F.data == "checkout")
    async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
        cart_data = await state.get_value("cart")
        if not cart_data or not cart_data.get("items"):
            await callback.answer("Корзина пуста", show_alert=True)
            return
        
        cart = Cart(**cart_data)
        
        checkout_text = f"<b>Оформление заказа</b>\n\n"
        checkout_text += f"Тип: {'Доставка' if cart.delivery_type == DeliveryTypeEnum.DELIVERY else 'Самовывоз'}\n"
        if cart.delivery_address:
            checkout_text += f"Адрес: {cart.delivery_address}\n"
        checkout_text += f"\n💰 Итого: {cart.total():.2f}₽\n\n"
        checkout_text += "Пожалуйста, подтвердите ваш номер телефона для оформления заказа."
        
        await callback.message.edit_text(
            checkout_text,
            reply_markup=BotKeyboards.checkout(cart.delivery_type)
        )

    @dp.message(F.contact)
    async def process_contact(message: types.Message, state: FSMContext, session: AsyncSession):
        phone = message.contact.phone_number
        
        # Update user phone
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        if user:
            await user_service.update_phone(user, phone)
        
        # Store phone in checkout state
        await state.update_value("checkout_phone", phone)
        
        # Proceed to order confirmation
        await confirm_order(message, state, session)

    @dp.callback_query(F.data == "confirm_order")
    async def confirm_order_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
        await confirm_order(callback.message, state, session)

    async def confirm_order(message: types.Message, state: FSMContext, session: AsyncSession):
        cart_data = await state.get_value("cart")
        if not cart_data or not cart_data.get("items"):
            await message.answer("Корзина пуста", reply_markup=BotKeyboards.main_menu())
            return
        
        cart = Cart(**cart_data)
        
        # Get user phone
        checkout_phone = await state.get_value("checkout_phone")
        if not checkout_phone:
            user_service = UserService(session)
            user = await user_service.get_by_telegram_id(str(message.from_user.id))
            checkout_phone = user.phone if user and user.phone else None
        
        if not checkout_phone and cart.delivery_type == DeliveryTypeEnum.DELIVERY:
            await message.answer(
                "Пожалуйста, укажите ваш номер телефона:",
                reply_markup=BotKeyboards.phone_request()
            )
            return
        
        # Create order
        order_data = OrderCreate(
            delivery_type=cart.delivery_type,
            delivery_address=cart.delivery_address,
            comment=cart.comment,
            items=cart.items
        )
        
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        order_service = OrderService(session)
        order = await order_service.create(order_data, user.id)
        
        # Clear cart
        await state.update_value("cart", None)
        await state.update_value("checkout_phone", None)
        
        order_text = f"✅ <b>Заказ #{order.id} оформлен!</b>\n\n"
        order_text += f"Статус: ⏳ Ожидает подтверждения\n"
        order_text += f"Тип: {'Доставка' if order.delivery_type.value == 'delivery' else 'Самовывоз'}\n"
        if order.delivery_address:
            order_text += f"Адрес: {order.delivery_address}\n"
        order_text += f"\n💰 Сумма: {order.total_amount:.2f}₽\n\n"
        order_text += "Мы уведомим вас о статусе заказа."
        
        await message.answer(order_text, reply_markup=BotKeyboards.order_status(order.id, order.status.value))

    @dp.message(F.text == "📦 Мои заказы")
    async def show_my_orders(message: types.Message, session: AsyncSession):
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start", reply_markup=BotKeyboards.main_menu())
            return
        
        order_service = OrderService(session)
        orders = await order_service.get_user_orders(user.id)
        
        if not orders:
            await message.answer("У вас пока нет заказов", reply_markup=BotKeyboards.main_menu())
            return
        
        await message.answer(
            "<b>Ваши заказы:</b>",
            reply_markup=BotKeyboards.my_orders(orders)
        )

    @dp.callback_query(F.data.startswith("order_detail_"))
    async def show_order_detail(callback: types.CallbackQuery, session: AsyncSession):
        order_id = int(callback.data.split("_")[2])
        
        order_service = OrderService(session)
        order = await order_service.get_by_id(order_id)
        
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        status_emoji = {
            "pending": "⏳ Ожидает",
            "confirmed": "✅ Подтвержден",
            "preparing": "👨‍🍳 Готовится",
            "ready": "🎉 Готов к выдаче",
            "delivering": "🚚 Доставляется",
            "completed": "⭐ Завершен",
            "cancelled": "❌ Отменен"
        }
        
        order_text = f"<b>Заказ #{order.id}</b>\n\n"
        order_text += f"Статус: {status_emoji.get(order.status.value, '📦')} \n"
        order_text += f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        order_text += f"Тип: {'Доставка' if order.delivery_type.value == 'delivery' else 'Самовывоз'}\n"
        if order.delivery_address:
            order_text += f"Адрес: {order.delivery_address}\n"
        order_text += f"\n<b>Товары:</b>\n"
        for item in order.items:
            order_text += f"• {item.product.name} x{item.quantity} - {item.price * item.quantity:.2f}₽\n"
        order_text += f"\n💰 Итого: {order.total_amount:.2f}₽"
        
        await callback.message.edit_text(
            order_text,
            reply_markup=BotKeyboards.order_status(order.id, order.status.value)
        )

    @dp.callback_query(F.data.startswith("cancel_order_"))
    async def cancel_order(callback: types.CallbackQuery, session: AsyncSession):
        order_id = int(callback.data.split("_")[2])
        
        order_service = OrderService(session)
        order = await order_service.get_by_id(order_id)
        
        if not order or order.status.value not in ["pending", "confirmed"]:
            await callback.answer("Нельзя отменить этот заказ", show_alert=True)
            return
        
        await order_service.cancel_order(order)
        
        await callback.message.edit_text(
            f"❌ Заказ #{order.id} отменен",
            reply_markup=BotKeyboards.back_to_menu()
        )

    @dp.callback_query(F.data == "back_to_menu")
    async def back_to_menu(callback: types.CallbackQuery):
        await callback.message.edit_text("Главное меню", reply_markup=BotKeyboards.main_menu())

    @dp.callback_query(F.data.startswith("back_to_products_"))
    async def back_to_products(callback: types.CallbackQuery, session: AsyncSession):
        category_id = int(callback.data.split("_")[3])
        
        product_service = ProductService(session)
        products = await product_service.get_by_category(category_id)
        
        await callback.message.edit_text(
            "<b>Выберите товар:</b>",
            reply_markup=BotKeyboards.products(products, category_id)
        )
