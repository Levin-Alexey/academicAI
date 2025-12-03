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

# ARQ Queue Configuration (используем отдельную БД для очередей)
ARQ_REDIS_HOST = os.getenv("ARQ_REDIS_HOST", REDIS_HOST)
ARQ_REDIS_PORT = int(os.getenv("ARQ_REDIS_PORT", str(REDIS_PORT)))
ARQ_REDIS_PASSWORD = os.getenv("ARQ_REDIS_PASSWORD", REDIS_PASSWORD)
ARQ_REDIS_DATABASE = int(os.getenv("ARQ_REDIS_DATABASE", "1"))  # БД 1 для очередей, БД 0 для контекста

# Allowed Users (список разрешенных Telegram ID)
ALLOWED_USERS = [
    # Добавьте ваши Telegram ID через переменные окружения
    # или настройте через админ панель бота
]

# Models
DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Bot Settings
MAX_MESSAGE_LENGTH = 4000