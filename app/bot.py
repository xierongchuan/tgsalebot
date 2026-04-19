from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from app.core.config import settings
from app.core.database import init_db
from app.handlers.start_handlers import create_start_handlers
from app.handlers.user_handlers import create_user_handlers
from app.handlers.admin_handlers import create_admin_handlers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def setup_bot():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Create session factory
    from app.core.database import async_session_maker
    
    # Setup commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Показать меню"),
        BotCommand(command="cart", description="Корзина"),
        BotCommand(command="orders", description="Мои заказы"),
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="admin", description="Админ панель")
    ])
    
    # Initialize database
    await init_db()
    
    # Register handlers
    create_start_handlers(dp, async_session_maker)
    create_user_handlers(dp, async_session_maker)
    create_admin_handlers(dp, async_session_maker, settings.admin_username)
    
    return bot, dp


async def start_polling():
    bot, dp = await setup_bot()
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_polling())
