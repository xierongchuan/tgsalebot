from aiogram import Router, F, types
from aiogram.filters import Command
from app.keyboards.keyboards import BotKeyboards
from app.services.services import UserService
from app.schemas.schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


def create_start_handlers(dp: Router, session_factory):
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, session: AsyncSession):
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
            
            welcome_text = f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            welcome_text += "Мы рады видеть вас в нашем боте.\n"
            welcome_text += "Здесь вы можете заказать вкусный кофе и другие товары.\n\n"
            welcome_text += "Используйте меню ниже для навигации:"
            
            await message.answer(welcome_text, reply_markup=BotKeyboards.main_menu())
        else:
            welcome_back_text = f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            welcome_back_text += "Что будете заказывать сегодня?"
            
            await message.answer(welcome_back_text, reply_markup=BotKeyboards.main_menu())

    @dp.message(Command("admin"))
    async def cmd_admin(message: types.Message, session: AsyncSession):
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user or not user.is_admin:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await message.answer(
            "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
            reply_markup=BotKeyboards.admin_main()
        )

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        help_text = "<b>📖 Помощь</b>\n\n"
        help_text += "Доступные команды:\n"
        help_text += "/start - Запустить бота\n"
        help_text += "/menu - Показать меню\n"
        help_text += "/cart - Показать корзину\n"
        help_text += "/orders - Мои заказы\n"
        help_text += "/profile - Мой профиль\n"
        help_text += "/help - Эта справка\n\n"
        help_text += "Также вы можете использовать кнопки в меню."
        
        await message.answer(help_text)

    @dp.message(Command("menu"))
    async def cmd_menu(message: types.Message, session: AsyncSession):
        from app.services.services import CategoryService
        category_service = CategoryService(session)
        categories = await category_service.get_all()
        
        if not categories:
            await message.answer("Меню временно недоступно", reply_markup=BotKeyboards.main_menu())
            return
        
        menu_text = "<b>☕ Наше меню</b>\n\nВыберите категорию:"
        await message.answer(menu_text, reply_markup=BotKeyboards.categories(categories))

    @dp.message(Command("cart"))
    async def cmd_cart(message: types.Message, state):
        from aiogram.fsm.context import FSMContext
        cart_data = await state.get_value("cart")
        
        if not cart_data or not cart_data.get("items"):
            await message.answer("Ваша корзина пуста ☹️", reply_markup=BotKeyboards.main_menu())
            return
        
        from app.schemas.schemas import Cart
        cart = Cart(**cart_data)
        
        cart_text = f"<b>🛒 Ваша корзина</b>\n\n"
        for item in cart.items:
            cart_text += f"• {item.product_name} x{item.quantity} - {item.price * item.quantity:.2f}₽\n"
        cart_text += f"\n💰 Итого: {cart.total():.2f}₽"
        
        await message.answer(cart_text, reply_markup=BotKeyboards.cart(cart.items, cart.delivery_type))

    @dp.message(Command("orders"))
    async def cmd_orders(message: types.Message, session: AsyncSession):
        from app.services.services import OrderService
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user:
            await message.answer("Сначала запустите бота через /start", reply_markup=BotKeyboards.main_menu())
            return
        
        order_service = OrderService(session)
        orders = await order_service.get_user_orders(user.id)
        
        if not orders:
            await message.answer("У вас пока нет заказов", reply_markup=BotKeyboards.main_menu())
            return
        
        from app.keyboards.keyboards import BotKeyboards
        await message.answer(
            "<b>Ваши заказы:</b>",
            reply_markup=BotKeyboards.my_orders(orders)
        )

    @dp.message(Command("profile"))
    async def cmd_profile(message: types.Message, session: AsyncSession):
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(str(message.from_user.id))
        
        if not user:
            await message.answer("Сначала запустите бота через /start", reply_markup=BotKeyboards.main_menu())
            return
        
        profile_text = f"👤 <b>Ваш профиль</b>\n\n"
        profile_text += f"Имя: {user.first_name or 'Не указано'}\n"
        profile_text += f"Телефон: {user.phone or 'Не указан'}\n"
        profile_text += f"Адрес: {user.address or 'Не указан'}\n"
        
        await message.answer(profile_text, reply_markup=BotKeyboards.main_menu())
