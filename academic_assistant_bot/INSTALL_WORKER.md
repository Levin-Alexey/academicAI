# Инструкция по установке ARQ Worker на VDS

## Шаг 1: Обновите зависимости

```bash
cd /opt/academicAI/academic_assistant_bot
source venv/bin/activate
pip install -r requirements.txt
```

## Шаг 2: Добавьте настройки ARQ в .env

Откройте файл `.env` и добавьте эти строки:

```bash
nano /opt/academicAI/academic_assistant_bot/.env
```

Добавьте в конец файла:

```env
# ARQ Queue Configuration (для фоновых задач - БД 1)
ARQ_REDIS_HOST=89.169.37.119
ARQ_REDIS_PORT=6379
ARQ_REDIS_PASSWORD=RedisBot2025!
ARQ_REDIS_DATABASE=1
```

Сохраните: `Ctrl+O`, Enter, `Ctrl+X`

## Шаг 3: Установите systemd service для worker

```bash
# Скопируйте файл service в systemd
sudo cp /opt/academicAI/academic_assistant_bot/academic-worker.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск worker
sudo systemctl enable academic-worker

# Запустите worker
sudo systemctl start academic-worker
```

## Шаг 4: Проверьте статус

```bash
# Проверьте что worker запущен
sudo systemctl status academic-worker

# Посмотрите логи в реальном времени
sudo journalctl -u academic-worker -f
```

Вы должны увидеть:
```
🚀 Запуск ARQ Worker...
✅ ARQ Worker успешно запущен и готов к обработке задач
```

## Шаг 5: Перезапустите бота

```bash
# Перезапустите основной бот для применения изменений
sudo systemctl restart academic-bot

# Проверьте что бот работает
sudo systemctl status academic-bot
```

## Управление сервисами

```bash
# Остановить worker
sudo systemctl stop academic-worker

# Запустить worker
sudo systemctl start academic-worker

# Перезапустить worker
sudo systemctl restart academic-worker

# Просмотр логов
sudo journalctl -u academic-worker -n 100    # последние 100 строк
sudo journalctl -u academic-worker -f         # в реальном времени
sudo journalctl -u academic-worker --since "10 minutes ago"
```

## Проверка работы очереди

```bash
# Подключитесь к Redis БД 1 (для очередей)
redis-cli -h 89.169.37.119 -a RedisBot2025! -n 1

# Проверьте наличие очереди
KEYS arq:*

# Посмотрите количество задач в очереди
LLEN arq:queue

# Выход
exit
```

## Масштабирование (опционально)

Если нужно обрабатывать больше запросов одновременно, можно запустить несколько workers:

### Создайте шаблон service:

```bash
sudo nano /etc/systemd/system/academic-worker@.service
```

Вставьте (обратите внимание на `%i` в Description):

```ini
[Unit]
Description=Academic Assistant ARQ Worker %i
After=network.target
After=redis.service
Wants=redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/academicAI/academic_assistant_bot
Environment=PATH=/opt/academicAI/academic_assistant_bot/venv/bin
ExecStart=/opt/academicAI/academic_assistant_bot/venv/bin/arq worker.WorkerSettings
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=academic-worker-%i

NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/academicAI/academic_assistant_bot

[Install]
WantedBy=multi-user.target
```

### Запустите несколько инстансов:

```bash
sudo systemctl daemon-reload

# Запустите 3 worker инстанса
sudo systemctl enable academic-worker@1
sudo systemctl enable academic-worker@2
sudo systemctl enable academic-worker@3

sudo systemctl start academic-worker@1
sudo systemctl start academic-worker@2
sudo systemctl start academic-worker@3

# Проверьте статус всех workers
sudo systemctl status 'academic-worker@*'
```

## Troubleshooting

### Worker не запускается

```bash
# Проверьте логи
sudo journalctl -u academic-worker -n 50

# Проверьте что arq установлен
/opt/academicAI/academic_assistant_bot/venv/bin/pip list | grep arq

# Проверьте что Redis доступен
redis-cli -h 89.169.37.119 -a RedisBot2025! ping
```

### Задачи не обрабатываются

```bash
# Проверьте что worker работает
ps aux | grep arq

# Проверьте очередь
redis-cli -h 89.169.37.119 -a RedisBot2025! -n 1 LLEN arq:queue

# Проверьте логи worker
sudo journalctl -u academic-worker -f
```

### Очистить застрявшие задачи

```bash
# Подключитесь к Redis
redis-cli -h 89.169.37.119 -a RedisBot2025! -n 1

# Очистите все задачи
FLUSHDB

# Или удалите конкретную очередь
DEL arq:queue

# Выход
exit
```

## Мониторинг

### Создайте скрипт для мониторинга

```bash
nano /opt/academicAI/monitor-queue.sh
```

Вставьте:

```bash
#!/bin/bash
echo "=== Academic Bot Queue Monitor ==="
echo ""
echo "Bot Status:"
systemctl is-active academic-bot
echo ""
echo "Worker Status:"
systemctl is-active academic-worker
echo ""
echo "Queue Length:"
redis-cli -h 89.169.37.119 -a RedisBot2025! -n 1 LLEN arq:queue
echo ""
echo "Active Jobs:"
redis-cli -h 89.169.37.119 -a RedisBot2025! -n 1 KEYS "arq:job:*" | wc -l
```

Сделайте исполняемым:

```bash
chmod +x /opt/academicAI/monitor-queue.sh
```

Запускайте когда нужно:

```bash
/opt/academicAI/monitor-queue.sh
```

## Готово!

Теперь у вас работает:
- **Бот** (`academic-bot`) - принимает запросы от пользователей
- **Worker** (`academic-worker`) - обрабатывает запросы в фоне

Пользователи будут получать:
1. Мгновенное подтверждение что запрос принят
2. Результат автоматически отправится в чат через несколько минут
