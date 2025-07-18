from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="📝 Новая работа", callback_data="new_work")
    keyboard.button(text="⚙️ Настройки", callback_data="settings")
    keyboard.button(text="ℹ️ Помощь", callback_data="help")

    keyboard.adjust(1)  # По одной кнопке в ряд
    return keyboard.as_markup()


def get_settings_menu(current_model: str) -> InlineKeyboardMarkup:
    """Меню настроек с выбором модели"""
    keyboard = InlineKeyboardBuilder()

    # Кнопки выбора модели
    models = [
        ("🧠 DeepSeek", "deepseek/deepseek-chat-v3-0324:free"),
        ("🤖 Claude Sonnet 4", "anthropic/claude-sonnet-4"),
        ("💡 Gemini 2.0 Flash", "google/gemini-2.0-flash-001"),
        ("🌟 OpenAI: GPT-4.1 Mini", "openai/gpt-4.1-mini")
    ]

    for name, model_id in models:
        # Добавляем галочку к выбранной модели
        if current_model == model_id:
            name = f"✅ {name}"

        keyboard.button(text=name, callback_data=f"select_model:{model_id}")

    keyboard.button(text="⬅️ Назад", callback_data="back_to_main")
    keyboard.adjust(1)

    return keyboard.as_markup()


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в меню", callback_data="back_to_main")
    return keyboard.as_markup()