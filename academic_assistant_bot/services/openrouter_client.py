import aiohttp
import asyncio
from typing import List, Dict, Optional
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
from services.user_service import user_service
from services.context_service import context_service


class OpenRouterClient:
    """Упрощенный клиент для работы с OpenRouter API"""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://academic-bot.com",
            "X-Title": "Academic Assistant Bot"
        }

    async def generate_text(self, user_id: int, prompt: str, use_context: bool = True) -> str:
        """
        Генерация текста через OpenRouter с автоматическим получением модели из БД

        Args:
            user_id: ID пользователя в Telegram
            prompt: Пользовательский запрос
            use_context: Использовать ли контекст из Redis

        Returns:
            Сгенерированный текст
        """
        # ПОЛУЧАЕМ МОДЕЛЬ ИЗ БАЗЫ ДАННЫХ
        model = await user_service.get_user_model(user_id)

        # Системный промпт для академических работ
        system_prompt = """
Ты - профессиональный помощник для написания академических работ в российских вузах.

Твои принципы:
- Отвечай только на русском языке
- Используй академический стиль изложения
- Структурируй информацию логично
- Соблюдай требования к оформлению по ГОСТ
- Создавай качественные, детальные тексты

ВАЖНО ДЛЯ ФОРМАТИРОВАНИЯ:
- При создании таблиц используй точное выравнивание столбцов
- Для таблиц используй символы | для разделения столбцов
- Делай одинаковую ширину столбцов для ровного отображения
- Пример таблицы:
| Столбец 1       | Столбец 2       | Столбец 3       |
|-----------------|-----------------|-----------------|
| Данные 1        | Данные 2        | Данные 3        |

Когда пользователь просит структуру - создай подробный план работы.
Когда просит главу - пиши развернутый текст этой главы.
Помни контекст предыдущих сообщений для связности работы.
"""

        messages = [{"role": "system", "content": system_prompt}]

        # Получаем контекст из Redis если нужно
        if use_context:
            context = await context_service.get_context(user_id)
            if context:
                messages.extend(context)

        # Добавляем текущий запрос
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,  # ← МОДЕЛЬ ИЗ БАЗЫ ДАННЫХ!
            "messages": messages,
            "max_tokens": 40000,
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        generated_text = result["choices"][0]["message"]["content"]
                        
                        # Сохраняем контекст разговора в Redis
                        if use_context:
                            # Добавляем запрос пользователя
                            await context_service.add_message_to_context(user_id, "user", prompt)
                            # Добавляем ответ ассистента
                            await context_service.add_message_to_context(user_id, "assistant", generated_text)
                        
                        return generated_text
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API error: {response.status} - {error_text}")

        except asyncio.TimeoutError:
            raise Exception("Timeout: Запрос занял слишком много времени")
        except Exception as e:
            raise Exception(f"Ошибка при обращении к OpenRouter: {str(e)}")

    async def clear_user_context(self, user_id: int) -> bool:
        """
        Очистить контекст разговора пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True если очистка прошла успешно
        """
        return await context_service.clear_context(user_id)

    async def get_context_info(self, user_id: int) -> dict:
        """
        Получить информацию о контексте пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Информация о контексте
        """
        return await context_service.get_context_info(user_id)


# Создаем глобальный экземпляр клиента
openrouter_client = OpenRouterClient()