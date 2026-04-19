# Coffee Shop / Store / Delivery Bot

Полнофункциональный телеграм-бот для кофеен, магазинов и забегаловок с доставкой.

## Структура проекта

```
/
├── backend/          # Python FastAPI backend (админка + API)
├── frontend/         # TypeScript React админ-панель
└── bot/             # Python Telegram бот для клиентов
```

## Функционал

### Для клиентов (Telegram бот):
- 📱 Просмотр меню с категориями
- 🛒 Корзина заказов
- 🚚 Выбор типа получения: самовывоз или доставка
- 📍 Геолокация для доставки
- ⏰ Отложенные заказы
- 💳 Оплата (карта/наличные)
- 📋 История заказов
- ⭐ Избранное
- 🔔 Уведомления о статусе заказа

### Для администраторов (Web панель):
- 📊 Управление меню (товары, категории, цены)
- 📝 Управление заказами в реальном времени
- 👥 Управление клиентами
- 🚚 Управление зонами доставки
- 📈 Статистика и аналитика
- 👨‍💼 Роли сотрудников (админ, оператор, курьер)
- 🏪 Управление филиалами

## Технологии

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Redis (кэш)
- JWT Authentication

### Frontend
- TypeScript
- React 18
- Vite
- Zustand (state management)
- TailwindCSS

### Bot
- Python 3.11+
- aiogram 3.x
- SQLAlchemy

## Быстрый старт

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Bot
```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Лицензия
MIT
