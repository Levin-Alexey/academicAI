from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

# создаём движок
engine = create_async_engine(DATABASE_URL, echo=True)

# базовый класс для моделей
class Base(DeclarativeBase):
    pass

# фабрика сессий
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# функция для получения сессии
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session