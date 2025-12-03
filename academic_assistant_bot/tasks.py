"""
Задачи для ARQ worker - обработка долгих операций в фоне
"""
import io
import logging
from aiogram import Bot
from aiogram.types import BufferedInputFile
from services.openrouter_client import openrouter_client
from keyboards.main_menu import get_back_button


logger = logging.getLogger(__name__)


async def process_llm_request(ctx, user_id: int, chat_id: int, prompt: str):
    """
    Фоновая задача для обработки запросов к LLM через OpenRouter

    Args:
        ctx: Контекст ARQ (содержит bot instance и другие данные)
        user_id: ID пользователя в Telegram
        chat_id: ID чата для отправки результата
        prompt: Текст запроса пользователя
    """
    logger.info(f"Начата обработка запроса для user_id={user_id}, chat_id={chat_id}")

    try:
        # Получаем bot instance из контекста
        bot: Bot = ctx['bot']

        # Отправляем статус "печатает" (будет активен 5 секунд)
        await bot.send_chat_action(chat_id, "typing")

        # Получаем ответ от LLM через OpenRouter (может занять до 120 секунд)
        logger.info(f"Отправка запроса в OpenRouter для user_id={user_id}")
        response = await openrouter_client.generate_text(user_id, prompt)
        logger.info(f"Получен ответ от OpenRouter для user_id={user_id}, длина: {len(response)} символов")

        # Создаем txt файл (удаляем символы * для чистого текста)
        clean_response = response.replace('*', '')
        txt_content = clean_response.encode('utf-8')
        txt_file = BufferedInputFile(txt_content, filename="response.txt")

        # Отправляем файл пользователю
        await bot.send_document(
            chat_id,
            txt_file,
            caption="📄 Ваш текст готов!",
            reply_markup=get_back_button()
        )

        # Также отправляем короткое сообщение с началом ответа
        preview = response[:500] + "..." if len(response) > 500 else response
        await bot.send_message(
            chat_id,
            f"📝 Краткий предварительный просмотр:\n\n{preview}"
        )

        logger.info(f"Результат успешно отправлен пользователю user_id={user_id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса для user_id={user_id}: {str(e)}", exc_info=True)

        # Отправляем сообщение об ошибке пользователю
        try:
            bot: Bot = ctx['bot']
            await bot.send_message(
                chat_id,
                f"❌ Произошла ошибка при генерации текста:\n{str(e)}\n\n"
                "Попробуйте еще раз или обратитесь к администратору.",
                reply_markup=get_back_button()
            )
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {str(send_error)}")
