from sqlalchemy import select
from database.session import async_session
from database.models import AllowedUsers


class AccessService:
    """Сервис для управления доступом пользователей"""

    @staticmethod
    async def is_user_allowed(telegram_id: int) -> bool:
        """
        Проверить, разрешен ли доступ пользователю
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            True если доступ разрешен
        """
        async with async_session() as session:
            result = await session.execute(
                select(AllowedUsers).where(
                    AllowedUsers.telegram_id == telegram_id,
                    AllowedUsers.is_active == True
                )
            )
            allowed_user = result.scalar_one_or_none()
            return allowed_user is not None

    @staticmethod
    async def add_allowed_user(telegram_id: int, first_name: str = None, username: str = None) -> bool:
        """
        Добавить пользователя в список доверенных
        
        Args:
            telegram_id: Telegram ID пользователя
            first_name: Имя пользователя
            username: Username пользователя
            
        Returns:
            True если пользователь добавлен успешно
        """
        try:
            async with async_session() as session:
                # Проверяем, не существует ли уже такой пользователь
                existing = await session.execute(
                    select(AllowedUsers).where(AllowedUsers.telegram_id == telegram_id)
                )
                
                if existing.scalar_one_or_none():
                    # Пользователь уже существует, активируем его
                    user = existing.scalar_one()
                    user.is_active = True
                    user.first_name = first_name
                    user.username = username
                else:
                    # Создаем нового пользователя
                    new_user = AllowedUsers(
                        telegram_id=telegram_id,
                        first_name=first_name,
                        username=username,
                        is_active=True
                    )
                    session.add(new_user)
                
                await session.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка добавления пользователя {telegram_id}: {e}")
            return False

    @staticmethod
    async def remove_allowed_user(telegram_id: int) -> bool:
        """
        Удалить пользователя из списка доверенных (деактивировать)
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            True если пользователь деактивирован успешно
        """
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(AllowedUsers).where(AllowedUsers.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    user.is_active = False
                    await session.commit()
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"Ошибка деактивации пользователя {telegram_id}: {e}")
            return False

    @staticmethod
    async def get_all_allowed_users() -> list:
        """
        Получить список всех доверенных пользователей
        
        Returns:
            Список объектов AllowedUsers
        """
        async with async_session() as session:
            result = await session.execute(
                select(AllowedUsers).where(AllowedUsers.is_active == True)
            )
            return result.scalars().all()



# Создаем глобальный экземпляр сервиса
access_service = AccessService()