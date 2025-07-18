from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu, get_settings_menu, get_back_button
from services.user_service import user_service
from utils.states import WorkStates

router = Router()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Команда /start - показываем главное меню"""
    await state.clear()  # Очищаем состояние
    await message.answer(
        "🎓 Добро пожаловать в академического помощника!\n\n"
        "Я помогу вам с написанием курсовых, дипломных работ и других академических текстов.\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()  # Очищаем состояние
    await callback.message.edit_text(
        "🎓 Добро пожаловать в академического помощника!\n\n"
        "Я помогу вам с написанием курсовых, дипломных работ и других академических текстов.\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):
    """Показать меню настроек"""
    user_id = callback.from_user.id

    # Получаем текущую модель пользователя через user_service
    current_model = await user_service.get_user_model(user_id)

    await callback.message.edit_text(
        f"⚙️ Настройки\n\n"
        f"Текущая модель: {current_model}\n\n"
        f"Выберите модель для генерации текста:",
        reply_markup=get_settings_menu(current_model)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_model:"))
async def select_model(callback: CallbackQuery):
    """Выбор модели LLM"""
    user_id = callback.from_user.id
    selected_model = callback.data.split(":")[1]

    # Сохраняем выбор в БД через user_service
    await user_service.save_user_model(user_id, selected_model)

    # Обновляем меню с новой выбранной моделью
    await callback.message.edit_text(
        f"⚙️ Настройки\n\n"
        f"Текущая модель: {selected_model}\n\n"
        f"Выберите модель для генерации текста:",
        reply_markup=get_settings_menu(selected_model)
    )
    await callback.answer("✅ Модель сохранена!")


@router.callback_query(F.data == "help")
async def help_menu(callback: CallbackQuery):
    """Показать помощь"""
    help_text = """
📚 Помощь по использованию бота

🎯 Возможности:
• Написание курсовых работ
• Создание дипломных проектов  
• Помощь с рефератами и эссе
• Структурирование материала
• Проверка и улучшение текста

🤖 Доступные модели:
• DeepSeek - быстрая и эффективная
• Claude Sonnet 4 - отличная для академических текстов
• Gemini 2.0 Flash - от Google, высокая скорость
• OpenAI GPT-4.1 Mini - компактная версия GPT-4

💡 Как пользоваться:
1. Нажмите "Новая работа"
2. Опишите задание
3. Получите помощь в написании

⚙️ В настройках можно выбрать предпочитаемую модель ИИ.
    """

    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "new_work")
async def new_work(callback: CallbackQuery, state: FSMContext):
    """Начать новую работу"""
    await state.set_state(WorkStates.waiting_for_message)
    await callback.message.edit_text(
        "📝 Создание новой работы\n\n"
        "Напишите ваш запрос. Например:\n"
        "• 'Создай структуру курсовой работы на тему...'\n"
        "• 'Напиши введение к дипломной работе...'\n"
        "• 'Подготовь главу 1 по теме...'\n\n"
        "Я отвечу и отправлю результат в виде .txt файла:",
        reply_markup=get_back_button()
    )
    await callback.answer()