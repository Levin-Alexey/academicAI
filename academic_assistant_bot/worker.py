"""
ARQ Worker для обработки фоновых задач
Запускается отдельным процессом: arq worker.WorkerSettings
"""
import logging
from aiogram import Bot
from arq.connections import RedisSettings
from config import BOT_TOKEN, ARQ_REDIS_HOST, ARQ_REDIS_PORT, ARQ_REDIS_PASSWORD, ARQ_REDIS_DATABASE
from tasks import process_llm_request


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def startup(ctx):
    """
    Функция вызывается при запуске worker
    Инициализирует bot instance и добавляет его в контекст
    """
    logger.info("🚀 Запуск ARQ Worker...")

    # Создаем bot instance для отправки сообщений
    bot = Bot(token=BOT_TOKEN)
    ctx['bot'] = bot

    logger.info("✅ ARQ Worker успешно запущен и готов к обработке задач")


async def shutdown(ctx):
    """
    Функция вызывается при остановке worker
    Закрывает соединения
    """
    logger.info("🛑 Остановка ARQ Worker...")

    # Закрываем bot session
    bot: Bot = ctx.get('bot')
    if bot:
        await bot.session.close()

    logger.info("✅ ARQ Worker остановлен")


class WorkerSettings:
    """
    Настройки для ARQ Worker
    """
    # Настройки подключения к Redis
    redis_settings = RedisSettings(
        host=ARQ_REDIS_HOST,
        port=ARQ_REDIS_PORT,
        password=ARQ_REDIS_PASSWORD,
        database=ARQ_REDIS_DATABASE,
    )

    # Список функций-задач, которые может выполнять worker
    functions = [process_llm_request]

    # Функции жизненного цикла
    on_startup = startup
    on_shutdown = shutdown

    # Настройки производительности
    max_jobs = 5  # Максимальное количество одновременных задач
    job_timeout = 300  # Таймаут выполнения задачи (5 минут)
    keep_result = 3600  # Время хранения результата в Redis (1 час)

    # Настройки повторных попыток
    max_tries = 3  # Максимальное количество попыток выполнения задачи
    retry_jobs = True  # Повторять задачи при ошибках

    # Имя очереди (по умолчанию "arq:queue")
    queue_name = "arq:queue"


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║        ARQ Worker для Academic Assistant Bot              ║
    ╚════════════════════════════════════════════════════════════╝

    Для запуска worker используйте команду:

        arq worker.WorkerSettings

    Worker будет обрабатывать задачи из Redis очереди.
    Убедитесь что Redis сервер запущен!

    Настройки:
    - Redis: {host}:{port} (БД: {db})
    - Max jobs: {max_jobs}
    - Timeout: {timeout}s
    - Queue: {queue}
    """.format(
        host=ARQ_REDIS_HOST,
        port=ARQ_REDIS_PORT,
        db=ARQ_REDIS_DATABASE,
        max_jobs=WorkerSettings.max_jobs,
        timeout=WorkerSettings.job_timeout,
        queue=WorkerSettings.queue_name
    ))
