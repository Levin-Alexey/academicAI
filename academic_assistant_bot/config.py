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

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Allowed Users (список разрешенных Telegram ID)
ALLOWED_USERS = [
    # Добавьте ваши Telegram ID через переменные окружения
    # или настройте через админ панель бота
]

# Models
DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Bot Settings
MAX_MESSAGE_LENGTH = 4000