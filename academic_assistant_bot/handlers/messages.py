import io
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from utils.states import WorkStates
from services.openrouter_client import openrouter_client
from keyboards.main_menu import get_back_button

router = Router()


@router.message(WorkStates.waiting_for_message)
async def handle_work_message(message: Message, state: FSMContext):
    """Обработка сообщений в режиме работы"""
    user_id = message.from_user.id
    user_message = message.text

    # Отправляем "печатает"
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Получаем ответ от LLM через OpenRouter
        response = await openrouter_client.generate_text(user_id, user_message)

        # Создаем txt файл
        txt_content = response.encode('utf-8')
        txt_file = BufferedInputFile(txt_content, filename="response.txt")

        # Отправляем файл пользователю
        await message.answer_document(
            txt_file,
            caption="📄 Ваш текст готов!",
            reply_markup=get_back_button()
        )

        # Также отправляем короткое сообщение с началом ответа
        preview = response[:500] + "..." if len(response) > 500 else response
        await message.answer(f"📝 Краткий предварительный просмотр:\n\n{preview}")

    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при генерации текста:\n{str(e)}\n\n"
            "Попробуйте еще раз или обратитесь к администратору.",
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