import io
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from arq import create_pool
from arq.connections import RedisSettings

from utils.states import WorkStates
from services.openrouter_client import openrouter_client
from keyboards.main_menu import get_back_button
from config import ARQ_REDIS_HOST, ARQ_REDIS_PORT, ARQ_REDIS_PASSWORD, ARQ_REDIS_DATABASE

router = Router()


@router.message(WorkStates.waiting_for_message)
async def handle_work_message(message: Message, state: FSMContext):
    """Обработка сообщений в режиме работы - ставит задачу в очередь ARQ"""
    user_id = message.from_user.id
    user_message = message.text

    try:
        # Создаем подключение к Redis для ARQ
        redis = await create_pool(
            RedisSettings(
                host=ARQ_REDIS_HOST,
                port=ARQ_REDIS_PORT,
                password=ARQ_REDIS_PASSWORD,
                database=ARQ_REDIS_DATABASE,
            )
        )

        # Ставим задачу в очередь
        job = await redis.enqueue_job(
            'process_llm_request',  # Имя функции из tasks.py
            user_id,
            message.chat.id,
            user_message
        )

        # Закрываем соединение
        await redis.close()

        # Отправляем подтверждение пользователю
        await message.answer(
            "⏳ Ваш запрос принят в обработку!\n\n"
            "Генерация текста может занять несколько минут.\n"
            "Результат будет отправлен автоматически в этот чат.\n\n"
            f"📋 ID задачи: `{job.job_id}`",
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )

    except Exception as e:
        # Если не удалось поставить задачу в очередь
        await message.answer(
            f"❌ Произошла ошибка при постановке задачи в очередь:\n{str(e)}\n\n"
            "Убедитесь что Redis сервер запущен и worker работает.",
            reply_markup=get_back_button()
        )


@router.message()
async def handle_other_messages(message: Message):
    """Обработка всех остальных сообщений"""
    await message.answer(
        "🤔 Сначала нажмите кнопку '📝 Новая работа' для начала диалога.\n\n"
        "Или используйте /start для возврата в главное меню.",
        reply_markup=get_back_button()
    )