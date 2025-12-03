# Руководство по запуску ARQ Worker

## Обзор

Проект использует **ARQ (Async Redis Queue)** для обработки долгих запросов к OpenRouter в фоновом режиме. Это решает проблему таймаутов Telegram и улучшает user experience.

### Архитектура

```
User → Telegram → Bot Handler → Redis Queue → ARQ Worker → OpenRouter API
                       ↓                             ↓
                  Ответ сразу              Отправка результата
```

## Требования

1. Redis сервер (уже используется для контекста)
2. Python пакет `arq==0.26.1` (добавлен в requirements.txt)

## Установка

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Настройте переменные окружения

В файле `.env` добавьте (или оставьте значения по умолчанию):

```env
# ARQ Queue Configuration
ARQ_REDIS_HOST=localhost
ARQ_REDIS_PORT=6379
ARQ_REDIS_PASSWORD=your_redis_password
ARQ_REDIS_DATABASE=1  # Используем БД 1 для очередей, БД 0 для контекста
```

## Запуск

### Вариант 1: Локальная разработка

Откройте **два терминала**:

**Терминал 1 - Telegram Bot:**
```bash
python main.py
```

**Терминал 2 - ARQ Worker:**
```bash
arq worker.WorkerSettings
```

### Вариант 2: Production с systemd (рекомендуется)

#### Создайте systemd service для бота

`/etc/systemd/system/academic-bot.service`:
```ini
[Unit]
Description=Academic Assistant Telegram Bot
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/academic_assistant_bot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Создайте systemd service для worker

`/etc/systemd/system/academic-worker.service`:
```ini
[Unit]
Description=Academic Assistant ARQ Worker
After=network.target redis.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/academic_assistant_bot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/arq worker.WorkerSettings
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Запустите сервисы

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Запустите сервисы
sudo systemctl start academic-bot
sudo systemctl start academic-worker

# Включите автозапуск
sudo systemctl enable academic-bot
sudo systemctl enable academic-worker

# Проверьте статус
sudo systemctl status academic-bot
sudo systemctl status academic-worker

# Просмотр логов
sudo journalctl -u academic-bot -f
sudo journalctl -u academic-worker -f
```

### Вариант 3: Production с supervisor

#### Установите supervisor

```bash
sudo apt-get install supervisor
```

#### Настройте bot

`/etc/supervisor/conf.d/academic-bot.conf`:
```ini
[program:academic-bot]
command=/path/to/venv/bin/python main.py
directory=/path/to/academic_assistant_bot
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/academic-bot.err.log
stdout_logfile=/var/log/academic-bot.out.log
```

#### Настройте worker

`/etc/supervisor/conf.d/academic-worker.conf`:
```ini
[program:academic-worker]
command=/path/to/venv/bin/arq worker.WorkerSettings
directory=/path/to/academic_assistant_bot
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/academic-worker.err.log
stdout_logfile=/var/log/academic-worker.out.log
```

#### Запустите

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start academic-bot
sudo supervisorctl start academic-worker

# Проверка статуса
sudo supervisorctl status
```

## Масштабирование

### Запуск нескольких workers

Для обработки большего количества запросов одновременно, запустите несколько worker процессов:

```bash
# Терминал 1
arq worker.WorkerSettings

# Терминал 2
arq worker.WorkerSettings

# Терминал 3
arq worker.WorkerSettings
```

Или в systemd создайте несколько сервисов:
```bash
/etc/systemd/system/academic-worker@.service
```

И запустите:
```bash
sudo systemctl start academic-worker@1
sudo systemctl start academic-worker@2
sudo systemctl start academic-worker@3
```

### Настройка производительности

В `worker.py` можно изменить:

```python
class WorkerSettings:
    max_jobs = 5  # Количество одновременных задач на worker
    job_timeout = 300  # Таймаут задачи (5 минут)
    max_tries = 3  # Количество попыток при ошибке
```

## Мониторинг

### Проверка очереди Redis

```bash
redis-cli -n 1  # Подключаемся к БД 1 (ARQ)

# Посмотреть все ключи очереди
KEYS arq:*

# Количество задач в очереди
LLEN arq:queue

# Просмотр задач
LRANGE arq:queue 0 -1
```

### Логи worker

ARQ worker выводит подробные логи:
- `🚀 Запуск ARQ Worker...` - worker запущен
- `Начата обработка запроса для user_id=...` - начало обработки
- `Получен ответ от OpenRouter...` - ответ получен
- `Результат успешно отправлен пользователю` - успех

## Troubleshooting

### Worker не запускается

**Проблема:** `ModuleNotFoundError: No module named 'arq'`
```bash
pip install arq==0.26.1
```

**Проблема:** `Connection refused` (Redis)
```bash
# Проверьте что Redis запущен
sudo systemctl status redis
sudo systemctl start redis
```

### Задачи не обрабатываются

1. Проверьте что worker запущен:
```bash
ps aux | grep arq
```

2. Проверьте логи worker:
```bash
# Если используется systemd
sudo journalctl -u academic-worker -f

# Если используется supervisor
tail -f /var/log/academic-worker.out.log
```

3. Проверьте очередь в Redis:
```bash
redis-cli -n 1 LLEN arq:queue
```

### Ошибки при отправке результатов

Если worker успешно генерирует текст, но не может отправить результат пользователю, проверьте:

1. `BOT_TOKEN` в `.env` корректен
2. Bot имеет права отправлять сообщения в чат
3. Проверьте логи на наличие `403 Forbidden` или `400 Bad Request`

## Откат к старой версии (без очереди)

Если нужно временно вернуться к синхронной обработке, замените в `handlers/messages.py`:

```python
# Было (с очередью):
job = await redis.enqueue_job('process_llm_request', ...)

# Стало (без очереди):
response = await openrouter_client.generate_text(user_id, user_message)
# ... отправка результата
```

## Полезные команды

```bash
# Остановить все workers
pkill -f "arq worker"

# Очистить очередь Redis
redis-cli -n 1 FLUSHDB

# Статистика Redis
redis-cli -n 1 INFO

# Количество задач в процессе
redis-cli -n 1 KEYS "arq:job:*" | wc -l
```

## Дополнительная информация

- [ARQ документация](https://arq-docs.helpmanual.io/)
- [Redis документация](https://redis.io/documentation)
- Telegram: ограничение `send_chat_action` - 5 секунд
- OpenRouter timeout в проекте: 300 секунд (config в `services/openrouter_client.py:88`)
