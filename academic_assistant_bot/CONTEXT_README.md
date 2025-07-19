# Система контекста для Academic Assistant Bot

## Описание

Система контекста позволяет боту запоминать предыдущие сообщения пользователей и использовать их для генерации более связных и контекстуально правильных ответов.

## Компоненты

### 1. ContextService (`services/context_service.py`)

Основной сервис для работы с контекстом разговоров:

- **save_context(user_id, context, ttl)** - сохранить контекст
- **get_context(user_id)** - получить контекст пользователя
- **add_message_to_context(user_id, role, content, max_messages)** - добавить сообщение
- **clear_context(user_id)** - очистить контекст
- **get_context_info(user_id)** - получить информацию о контексте

### 2. OpenRouterClient (обновлен)

Клиент для работы с LLM теперь автоматически:

- Загружает контекст из Redis перед генерацией
- Сохраняет новые сообщения в контекст после генерации
- Предоставляет методы для управления контекстом

### 3. Обновленное меню

Добавлена кнопка "🗑️ Очистить контекст" в главное меню.

## Конфигурация

В `config.py` добавлены настройки Redis:

```python
# Redis Configuration
REDIS_HOST = "89.169.37.119"
REDIS_PORT = 6379
REDIS_PASSWORD = "RedisBot2025!"
```

## Использование

### Автоматическое сохранение контекста

```python
# Генерация с автоматическим сохранением контекста
response = await openrouter_client.generate_text(
    user_id=user_id, 
    prompt="Привет! Как дела?",
    use_context=True  # По умолчанию True
)
```

### Ручное управление контекстом

```python
from services.context_service import context_service

# Добавить сообщение
await context_service.add_message_to_context(
    user_id=123456,
    role="user", 
    content="Привет!"
)

# Получить контекст
context = await context_service.get_context(user_id=123456)

# Очистить контекст
await context_service.clear_context(user_id=123456)

# Получить информацию
info = await context_service.get_context_info(user_id=123456)
```

### Информация о контексте

```python
info = await context_service.get_context_info(user_id)
# Возвращает:
{
    "user_id": 123456,
    "messages_count": 5,
    "ttl_seconds": 3599,
    "has_context": True
}
```

## Настройки

- **TTL контекста**: 3600 секунд (1 час) по умолчанию
- **Максимум сообщений**: 10 сообщений на пользователя
- **Формат сообщений**: `{"role": "user/assistant", "content": "текст"}`

## Логика работы

1. Пользователь отправляет сообщение
2. Бот загружает существующий контекст из Redis
3. Добавляет контекст в запрос к LLM
4. Получает ответ от LLM
5. Сохраняет запрос и ответ в контекст
6. Ограничивает контекст максимальным количеством сообщений

## Тестирование

Запустите тест:
```bash
python services/context_service.py
```

Или используйте тестовый скрипт Redis:
```bash
python test_redis.py
```

## Структура контекста

```json
[
    {"role": "user", "content": "Привет! Помоги с курсовой"},
    {"role": "assistant", "content": "Привет! Конечно помогу..."},
    {"role": "user", "content": "Тема: Искусственный интеллект"},
    {"role": "assistant", "content": "Отличная тема! Вот структура..."}
]
```

## Преимущества

1. **Связность диалога** - бот помнит предыдущие сообщения
2. **Персонализация** - каждый пользователь имеет свой контекст  
3. **Эффективность** - автоматическое управление памятью
4. **Надежность** - данные хранятся в Redis с TTL
5. **Масштабируемость** - поддержка множества пользователей

## Мониторинг

Используйте Redis CLI для мониторинга:
```bash
# Подключение к Redis
redis-cli -h 89.169.37.119 -p 6379 -a RedisBot2025!

# Просмотр ключей контекста
KEYS context_*

# Просмотр конкретного контекста
GET context_123456

# Просмотр TTL
TTL context_123456
```