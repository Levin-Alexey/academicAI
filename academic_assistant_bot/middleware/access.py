from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from services.access_service import access_service


class AccessMiddleware(BaseMiddleware):
    """Middleware для проверки доступа пользователей через базу данных"""

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        # Получаем ID пользователя
        user_id = event.from_user.id

        # Проверяем доступ через базу данных
        is_allowed = await access_service.is_user_allowed(user_id)
        
        if not is_allowed:
            if isinstance(event, Message):
                await event.answer(
                    "🔒 Этот бот является закрытым и доступен только для определенного круга пользователей.\n\n"
                    "Если вы считаете, что у вас должен быть доступ, обратитесь к администратору."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("🔒 Доступ запрещен", show_alert=True)

            return  # Прерываем выполнение

        # Если доступ разрешен, продолжаем
        return await handler(event, data)