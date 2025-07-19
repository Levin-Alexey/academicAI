# 🎓 Академический помощник - Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.4.1-green.svg)](https://aiogram.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-6.0+-red.svg)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Умный Telegram-бот для создания курсовых, дипломных работ и других академических текстов с использованием искусственного интеллекта.**

---

## 🚀 Быстрый старт

### Для пользователей:
1. Найдите бота в Telegram: **@akademforwork_bot**
2. Нажмите `/start`
3. Выберите "📝 Новая работа"
4. Опишите, что вам нужно
5. Получите готовый результат!

### Для разработчиков:
```bash
git clone https://github.com/your-repo/academic_assistant_bot.git
cd academic_assistant_bot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Настройте переменные в .env
python main.py
```

---

## 📋 Возможности

### 🤖 Искусственный интеллект
- **4 различные модели ИИ**: DeepSeek, Claude Sonnet 4, Gemini 2.0 Flash, OpenAI GPT-4.1 Mini
- **Переключение между моделями** в зависимости от задачи
- **Качественная генерация** академических текстов

### 📝 Типы академических работ
- **Курсовые работы** любой сложности и специальности
- **Дипломные проекты** с полной структурой
- **Рефераты и эссе** различного объема
- **Лабораторные отчеты** с анализом
- **Научные статьи** и обзоры литературы

### 💭 Умная память
- **Контекст разговора** сохраняется автоматически
- **Продолжение работы** через несколько дней
- **Связность текста** благодаря памяти предыдущих сообщений
- **Автоматическая очистка** устаревших данных

### 💾 Удобный вывод
- **Файлы .txt** с готовыми результатами
- **Прямая загрузка** через Telegram
- **Копирование в Word** одним кликом
- **Структурированный формат** для удобства использования

---

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │────│  Academic Bot   │────│   OpenRouter    │
│     Frontend    │    │     Backend     │    │      API        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
       │   PostgreSQL    │    │   Redis Cache   │    │   File System   │
       │    Database     │    │  (Context)      │    │   (Results)     │
       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🧩 Компоненты
- **main.py** - Точка входа приложения
- **handlers/** - Обработчики Telegram сообщений
- **services/** - Бизнес-логика и внешние API
- **database/** - Модели данных и сессии
- **keyboards/** - Интерфейс пользователя
- **middleware/** - Промежуточная обработка

---

## ⚙️ Технические требования

### Минимальные:
- **Python 3.10+**
- **RAM**: 4 GB
- **Диск**: 20 GB
- **CPU**: 2 ядра

### Рекомендуемые:
- **Python 3.11**
- **RAM**: 8 GB
- **Диск**: 50 GB SSD
- **CPU**: 4+ ядра

### Зависимости:
```txt
aiogram==3.4.1
aiohttp~=3.9.0
sqlalchemy==2.0.40
asyncpg==0.30.0
alembic==1.15.2
python-dotenv==1.1.0
pydantic==2.11.3
pydantic-settings==2.1.0
aiofiles~=23.2.1
redis==5.0.1
```

---

## 🔧 Настройка и установка

### 1. Подготовка окружения
```bash
# Клонирование репозитория
git clone https://github.com/your-repo/academic_assistant_bot.git
cd academic_assistant_bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE academic_bot;
CREATE USER bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE academic_bot TO bot_user;
```

### 3. Настройка Redis
```bash
# Установка Redis (Ubuntu)
sudo apt install redis-server

# Настройка пароля
redis-cli
CONFIG SET requirepass "your_redis_password"
CONFIG REWRITE
```

### 4. Конфигурация приложения
```bash
# Копирование и настройка переменных окружения
cp .env.example .env
nano .env
```

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://bot_user:password@localhost:5432/academic_bot

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### 5. Запуск приложения
```bash
# Создание таблиц в базе данных
python -c "import asyncio; from database.session import engine; from database.models import Base; asyncio.run(Base.metadata.create_all(engine))"

# Запуск бота
python main.py
```

---

## 🚀 Развертывание в продакшен

### Systemd сервис
```bash
# Создание сервиса
sudo nano /etc/systemd/system/academic-assistant-bot.service
```

```ini
[Unit]
Description=Academic Assistant Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/academic_assistant_bot
Environment=PATH=/opt/academic_assistant_bot/venv/bin
ExecStart=/opt/academic_assistant_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Активация и запуск
sudo systemctl daemon-reload
sudo systemctl enable academic-assistant-bot.service
sudo systemctl start academic-assistant-bot.service
```

### Docker (опционально)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

---

## 📊 Мониторинг

### Логи
```bash
# Просмотр логов
journalctl -u academic-assistant-bot.service -f

# Логи за сегодня
journalctl -u academic-assistant-bot.service --since today
```

### Состояние системы
```bash
# Статус сервисов
systemctl status academic-assistant-bot.service
systemctl status postgresql
systemctl status redis

# Использование ресурсов
htop
df -h
```

### База данных
```sql
-- Количество пользователей
SELECT COUNT(*) FROM users;

-- Активность за сегодня
SELECT COUNT(*) FROM deals WHERE DATE(created_at) = CURRENT_DATE;

-- Популярные модели
SELECT model_name, COUNT(*) FROM user_settings GROUP BY model_name;
```

---

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
python -m pytest

# Тесты с покрытием
python -m pytest --cov=.

# Тесты базы данных
python test_db_connection.py

# Тесты Redis
python test_redis.py
```

### Тестирование API
```bash
# Проверка Telegram Bot API
curl "https://api.telegram.org/bot$BOT_TOKEN/getMe"

# Проверка OpenRouter API
curl -X GET "https://openrouter.ai/api/v1/models" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## 📚 Документация

| Документ | Описание | Аудитория |
|----------|----------|-----------|
| [**БЫСТРЫЙ_СТАРТ.md**](БЫСТРЫЙ_СТАРТ.md) | Начало работы за 2 минуты | Пользователи |
| [**ПОЛЬЗОВАТЕЛЬСКАЯ_ДОКУМЕНТАЦИЯ.md**](ПОЛЬЗОВАТЕЛЬСКАЯ_ДОКУМЕНТАЦИЯ.md) | Полное руководство пользователя | Студенты |
| [**ТЕХНИЧЕСКАЯ_ДОКУМЕНТАЦИЯ.md**](ТЕХНИЧЕСКАЯ_ДОКУМЕНТАЦИЯ.md) | Архитектура и API | Разработчики |
| [**РУКОВОДСТВО_АДМИНИСТРАТОРА.md**](РУКОВОДСТВО_АДМИНИСТРАТОРА.md) | Установка и обслуживание | Администраторы |
| [**CHANGELOG.md**](CHANGELOG.md) | История изменений | Все |

---

## 🤝 Участие в разработке

### Как внести вклад
1. **Fork** репозитория
2. Создайте **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** изменения: `git commit -m 'Add amazing feature'`
4. **Push** в branch: `git push origin feature/amazing-feature`
5. Создайте **Pull Request**

### Стандарты кода
- **PEP 8** для Python кода
- **Type hints** обязательны
- **Docstrings** для всех функций
- **Tests** для новой функциональности

### Структура коммитов
```
feat: добавить новую модель ИИ
fix: исправить обработку ошибок API
docs: обновить документацию пользователя
style: форматирование кода
refactor: рефакторинг сервиса контекста
test: добавить тесты для базы данных
```

---

## 🐛 Сообщения об ошибках

### Перед созданием issue:
1. Проверьте [существующие issues](https://github.com/your-repo/academic_assistant_bot/issues)
2. Убедитесь, что используете последнюю версию
3. Проверьте логи: `journalctl -u academic-assistant-bot.service -n 50`

### Шаблон issue:
```markdown
**Описание проблемы:**
Краткое описание того, что произошло

**Шаги для воспроизведения:**
1. Шаг 1
2. Шаг 2
3. Шаг 3

**Ожидаемое поведение:**
Что должно было произойти

**Фактическое поведение:**
Что произошло на самом деле

**Окружение:**
- ОС: Ubuntu 22.04
- Python: 3.11
- Версия бота: 1.0.0

**Логи:**
```
Вставьте релевантные логи здесь
```
```

---

## 📈 Roadmap

### 🎯 Версия 1.1.0
- [ ] Dashboard администратора
- [ ] Статистика использования
- [ ] Экспорт в PDF формат
- [ ] Шаблоны работ

### 🚀 Версия 1.2.0
- [ ] Многоязычность (EN)
- [ ] Голосовые сообщения
- [ ] Интеграция с Google Docs
- [ ] Мобильное приложение

### 🌟 Версия 2.0.0
- [ ] REST API
- [ ] Веб-интерфейс
- [ ] Совместная работа
- [ ] Marketplace шаблонов

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

## 👥 Команда

### Основные разработчики
- **Backend Developer** - Архитектура и основной функционал
- **DevOps Engineer** - Инфраструктура и развертывание
- **Technical Writer** - Документация и пользовательский опыт

### Благодарности
- **aiogram community** за отличный фреймворк
- **OpenRouter** за доступ к моделям ИИ
- **PostgreSQL & Redis teams** за надежные решения

---

## 📞 Контакты

- **Telegram Bot**: [@akademforwork_bot](https://t.me/akademforwork_bot)
- **Issues**: [GitHub Issues](https://github.com/your-repo/academic_assistant_bot/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/academic_assistant_bot/wiki)
- **Email**: support@academicbot.com

---

## ⭐ Поддержите проект

Если проект оказался полезным:
- ⭐ **Поставьте звезду** на GitHub
- 🐛 **Сообщайте** об ошибках
- 💡 **Предлагайте** улучшения
- 📢 **Расскажите** друзьям

---

**Создано с ❤️ для студентов и преподавателей**

![Academic Bot](https://img.shields.io/badge/Academic-Bot-success?style=for-the-badge&logo=telegram)
![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=for-the-badge)
![Made with](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)