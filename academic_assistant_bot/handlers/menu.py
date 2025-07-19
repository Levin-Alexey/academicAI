from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu, get_settings_menu, get_back_button, get_user_management_menu
from services.user_service import user_service
from services.openrouter_client import openrouter_client
from services.access_service import access_service
from utils.states import WorkStates, UserManagementStates

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


@router.callback_query(F.data == "clear_context")
async def clear_context(callback: CallbackQuery):
    """Очистить контекст разговора"""
    user_id = callback.from_user.id
    
    # Получаем информацию о контексте
    context_info = await openrouter_client.get_context_info(user_id)
    
    if context_info['has_context']:
        # Очищаем контекст
        success = await openrouter_client.clear_user_context(user_id)
        
        if success:
            await callback.message.edit_text(
                f"✅ Контекст очищен!\n\n"
                f"Удалено сообщений: {context_info['messages_count']}\n"
                f"Теперь можете начать новый разговор.",
                reply_markup=get_main_menu()
            )
        else:
            await callback.message.edit_text(
                "❌ Ошибка при очистке контекста. Попробуйте еще раз.",
                reply_markup=get_main_menu()
            )
    else:
        await callback.message.edit_text(
            "ℹ️ Контекст уже пуст. Нет сообщений для удаления.",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "new_work")
async def new_work(callback: CallbackQuery, state: FSMContext):
    """Начать новую работу"""
    user_id = callback.from_user.id
    
    # Получаем информацию о контексте
    context_info = await openrouter_client.get_context_info(user_id)
    
    context_status = ""
    if context_info['has_context']:
        context_status = f"\n\n💬 Контекст: {context_info['messages_count']} сообщений"
    
    await state.set_state(WorkStates.waiting_for_message)
    await callback.message.edit_text(
        "📝 Создание новой работы\n\n"
        "Напишите ваш запрос. Например:\n"
        "• 'Создай структуру курсовой работы на тему...'\n"
        "• 'Напиши введение к дипломной работе...'\n"
        "• 'Подготовь главу 1 по теме...'\n\n"
        "Я отвечу и отправлю результат в виде .txt файла." + context_status,
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "user_management")
async def user_management_menu(callback: CallbackQuery):
    """Показать меню управления пользователями"""
    await callback.message.edit_text(
        "👥 Управление пользователями\n\n"
        "Выберите действие:",
        reply_markup=get_user_management_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "list_users")
async def list_users(callback: CallbackQuery):
    """Показать список доверенных пользователей"""
    try:
        users = await access_service.get_all_allowed_users()
        
        if not users:
            text = "📋 Список доверенных пользователей\n\n❌ Нет доверенных пользователей"
        else:
            text = f"📋 Список доверенных пользователей ({len(users)})\n\n"
            for i, user in enumerate(users, 1):
                name = user.first_name or "Неизвестно"
                username = f"@{user.username}" if user.username else "нет username"
                text += f"{i}. {name} ({username})\n"
                text += f"   ID: {user.telegram_id}\n"
                text += f"   Добавлен: {user.added_at.strftime('%d.%m.%Y')}\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_user_management_menu()
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка получения списка пользователей:\n{str(e)}",
            reply_markup=get_user_management_menu()
        )
    
    await callback.answer()


@router.message(UserManagementStates.waiting_for_user_id_to_add)
async def handle_add_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя для добавления"""
    try:
        # Валидация ID
        user_id_text = message.text.strip()
        
        if not user_id_text.isdigit():
            await message.answer(
                "❌ Ошибка: ID должен содержать только цифры.\n\n"
                "Попробуйте еще раз или нажмите 'Назад' для отмены.",
                reply_markup=get_user_management_menu()
            )
            return
        
        telegram_id = int(user_id_text)
        
        # Проверяем диапазон Telegram ID (обычно больше 1000)
        if telegram_id < 1000:
            await message.answer(
                "❌ Ошибка: ID слишком короткий. Telegram ID обычно содержит больше цифр.\n\n"
                "Попробуйте еще раз или нажмите 'Назад' для отмены.",
                reply_markup=get_user_management_menu()
            )
            return
        
        # Проверяем, не существует ли уже такой пользователь
        is_already_allowed = await access_service.is_user_allowed(telegram_id)
        if is_already_allowed:
            await message.answer(
                f"⚠️ Пользователь с ID {telegram_id} уже есть в списке доверенных.",
                reply_markup=get_user_management_menu()
            )
            await state.clear()
            return
        
        # Пытаемся получить информацию о пользователе
        try:
            user_info = await message.bot.get_chat(telegram_id)
            first_name = user_info.first_name or "Неизвестно"
            username = user_info.username
        except Exception:
            # Если не удалось получить информацию, используем базовые данные
            first_name = "Неизвестный пользователь"
            username = None
        
        # Добавляем пользователя
        success = await access_service.add_allowed_user(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username
        )
        
        if success:
            username_text = f"@{username}" if username else "нет username"
            await message.answer(
                f"✅ Пользователь успешно добавлен!\n\n"
                f"👤 Имя: {first_name}\n"
                f"🆔 ID: {telegram_id}\n"
                f"📝 Username: {username_text}",
                reply_markup=get_user_management_menu()
            )
        else:
            await message.answer(
                f"❌ Ошибка при добавлении пользователя {telegram_id}.\n"
                "Попробуйте еще раз позже.",
                reply_markup=get_user_management_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Ошибка: Неверный формат ID.\n\n"
            "Попробуйте еще раз или нажмите 'Назад' для отмены.",
            reply_markup=get_user_management_menu()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}\n\n"
            "Попробуйте еще раз или нажмите 'Назад' для отмены.",
            reply_markup=get_user_management_menu()
        )
        await state.clear()


@router.callback_query(F.data == "add_user")
async def add_user_start(callback: CallbackQuery, state: FSMContext):
    """Начать процесс добавления пользователя"""
    await state.set_state(UserManagementStates.waiting_for_user_id_to_add)
    await callback.message.edit_text(
        "➕ Добавление нового пользователя\n\n"
        "Отправьте Telegram ID пользователя (число), "
        "которого хотите добавить в список доверенных.\n\n"
        "Например: 123456789\n\n"
        "Или нажмите 'Назад' для отмены.",
        reply_markup=get_user_management_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "remove_user")
async def remove_user_start(callback: CallbackQuery):
    """Начать процесс удаления пользователя"""
    try:
        users = await access_service.get_all_allowed_users()
        
        if not users:
            text = "❌ Нет пользователей для удаления"
        else:
            text = "❌ Удаление пользователя\n\n"
            text += "Отправьте Telegram ID пользователя, которого хотите удалить:\n\n"
            for i, user in enumerate(users, 1):
                name = user.first_name or "Неизвестно"
                text += f"{i}. {name} - ID: {user.telegram_id}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_user_management_menu()
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка получения списка пользователей:\n{str(e)}",
            reply_markup=get_user_management_menu()
        )
    
    await callback.answer()


@router.message(UserManagementStates.waiting_for_user_id_to_add)
async def handle_add_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя для добавления"""
    try:
        # Валидация ID
        user_id_text = message.text.strip()
        
        if not user_id_text.isdigit():
            await message.answer(
                "❌ Ошибка: ID должен содержать только цифры.\n\n"
                "Попробуйте еще раз или нажмите 'Назад' для отмены.",
                reply_markup=get_user_management_menu()
            )
            return
        
        telegram_id = int(user_id_text)
        
        # Проверяем диапазон Telegram ID (обычно больше 1000)
        if telegram_id < 1000:
            await message.answer(
                "❌ Ошибка: ID слишком короткий. Telegram ID обычно содержит больше цифр.\n\n"
                "Попробуйте еще раз или нажмите 'Назад' для отмены.",
                reply_markup=get_user_management_menu()
            )
            return
        
        # Проверяем, не существует ли уже такой пользователь
        is_already_allowed = await access_service.is_user_allowed(telegram_id)
        if is_already_allowed:
            await message.answer(
                f"⚠️ Пользователь с ID {telegram_id} уже есть в списке доверенных.",
                reply_markup=get_user_management_menu()
            )
            await state.clear()
            return
        
        # Пытаемся получить информацию о пользователе
        try:
            user_info = await message.bot.get_chat(telegram_id)
            first_name = user_info.first_name or "Неизвестно"
            username = user_info.username
        except Exception:
            # Если не удалось получить информацию, используем базовые данные
            first_name = "Неизвестный пользователь"
            username = None
        
        # Добавляем пользователя
        success = await access_service.add_allowed_user(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username
        )
        
        if success:
            username_text = f"@{username}" if username else "нет username"
            await message.answer(
                f"✅ Пользователь успешно добавлен!\n\n"
                f"👤 Имя: {first_name}\n"
                f"🆔 ID: {telegram_id}\n"
                f"📝 Username: {username_text}",
                reply_markup=get_user_management_menu()
            )
        else:
            await message.answer(
                f"❌ Ошибка при добавлении пользователя {telegram_id}.\n"
                "Попробуйте еще раз позже.",
                reply_markup=get_user_management_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Ошибка: Неверный формат ID.\n\n"
            "Попробуйте еще раз или нажмите 'Назад' для отмены.",
            reply_markup=get_user_management_menu()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}\n\n"
            "Попробуйте еще раз или нажмите 'Назад' для отмены.",
            reply_markup=get_user_management_menu()
        )
        await state.clear()