from sqlalchemy import select
from database.session import async_session
from database.models import UserSettings
from config import DEFAULT_MODEL


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def get_user_model(user_id: int) -> str:
        """
        Получить выбранную модель пользователя из БД

        Args:
            user_id: Telegram ID пользователя

        Returns:
            Строка с названием модели (например, "deepseek/deepseek-chat-v3-0324:free")
        """
        async with async_session() as session:
            # Ищем настройки пользователя
            result = await session.execute(
                select(UserSettings.selected_model).where(
                    UserSettings.telegram_id == user_id
                )
            )

            # Получаем модель или возвращаем дефолтную
            user_model = result.scalar_one_or_none()

            if user_model:
                return user_model
            else:
                return DEFAULT_MODEL

    @staticmethod
    async def save_user_model(user_id: int, model: str) -> None:
        """
        Сохранить выбранную модель пользователя в БД

        Args:
            user_id: Telegram ID пользователя
            model: Название модели
        """
        async with async_session() as session:
            # Ищем существующие настройки
            result = await session.execute(
                select(UserSettings).where(UserSettings.telegram_id == user_id)
            )
            user_settings = result.scalar_one_or_none()

            if user_settings:
                # Обновляем существующие настройки
                user_settings.selected_model = model
            else:
                # Создаем новые настройки
                user_settings = UserSettings(
                    telegram_id=user_id,
                    selected_model=model
                )
                session.add(user_settings)

            await session.commit()

    @staticmethod
    async def get_user_settings(user_id: int) -> UserSettings:
        """
        Получить все настройки пользователя

        Args:
            user_id: Telegram ID пользователя

        Returns:
            Объект UserSettings или None
        """
        async with async_session() as session:
            result = await session.execute(
                select(UserSettings).where(UserSettings.telegram_id == user_id)
            )
            return result.scalar_one_or_none()


# Создаем глобальный экземпляр сервиса
user_service = UserService()