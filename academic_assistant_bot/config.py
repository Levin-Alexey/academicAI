from dotenv import load_dotenv
import os

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Allowed Users (список разрешенных Telegram ID)
ALLOWED_USERS = [
    525944420,  # Замените на реальные ID
    150333241,
    # Добавьте больше ID по необходимости
]

# Models
DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Bot Settings
MAX_MESSAGE_LENGTH = 4000