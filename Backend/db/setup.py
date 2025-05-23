# app/db/setup.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.models import Model  # Импортируем базовую модель ORM из нового расположения
from app.core.config import settings  # Импортируем настройки приложения

# Инициализация асинхронного движка SQLAlchemy
# Строка подключения берется из настроек приложения, что делает ее конфигурируемой
eng = create_async_engine(
    settings.DATABASE_URL,
)

# Создание фабрики асинхронных сессий для взаимодействия с базой данных
# expire_on_commit=False предотвращает автоматическое истечение срока действия объектов после коммита
new_session = async_sessionmaker(eng, expire_on_commit=False)


async def create_tables():
    """
    Создает все таблицы в базе данных, определенные в моделях SQLAlchemy.
    Вызывается при запуске приложения.
    """
    async with eng.begin() as conn:
        # conn.run_sync выполняет синхронную операцию в асинхронном контексте
        # Model.metadata.create_all создает все таблицы, связанные с Model.metadata
        await conn.run_sync(Model.metadata.create_all)
    print("Database tables created successfully.")


async def delete_tables():
    """
    Удаляет все таблицы из базы данных, определенные в моделях SQLAlchemy.
    Используйте с осторожностью, так как это приведет к потере всех данных.
    """
    async with eng.begin() as conn:
        # conn.run_sync выполняет синхронную операцию в асинхронном контексте
        # Model.metadata.drop_all удаляет все таблицы, связанные с Model.metadata
        await conn.run_sync(Model.metadata.drop_all)
    print("Database tables deleted successfully.")

# В реальном приложении функции create_tables и delete_tables
# обычно вызываются в Lifespan-событиях FastAPI (main.py)
# или через отдельные скрипты для миграции базы данных (например, Alembic).
