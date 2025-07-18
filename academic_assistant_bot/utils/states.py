from aiogram.fsm.state import State, StatesGroup


class WorkStates(StatesGroup):
    """Состояния для работы с академическими текстами"""
    waiting_for_message = State()  # Ожидание сообщения от пользователя