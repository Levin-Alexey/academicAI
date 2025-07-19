from aiogram.fsm.state import State, StatesGroup


class WorkStates(StatesGroup):
    """Состояния для работы с академическими текстами"""
    waiting_for_message = State()  # Ожидание сообщения от пользователя


class UserManagementStates(StatesGroup):
    """Состояния для управления пользователями"""
    waiting_for_user_id_to_add = State()     # Ожидание ID для добавления
    waiting_for_user_id_to_remove = State()  # Ожидание ID для удаления