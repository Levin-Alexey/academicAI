"""
Сервис для управления контекстом разговоров с LLM
"""

import json
import asyncio
from typing import List, Dict, Optional
from redis.asyncio import Redis
try:
    from config import REDIS_URL, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
except ImportError:
    # Для тестирования без config
    REDIS_URL = "redis://:RedisBot2025!@89.169.37.119:6379/0"
    REDIS_HOST = "89.169.37.119"
    REDIS_PORT = 6379
    REDIS_PASSWORD = "RedisBot2025!"

class ContextService:
    """Сервис для работы с контекстом разговоров"""
    
    def __init__(self):
        self.redis_url = REDIS_URL
        self.redis_host = REDIS_HOST
        self.redis_port = REDIS_PORT
        self.redis_password = REDIS_PASSWORD
        
    async def _get_redis_connection(self) -> Redis:
        """Получить соединение с Redis"""
        try:
            # Пробуем подключиться через URL (современный способ)
            return Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
        except Exception:
            # Fallback на старый способ подключения
            return Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
    
    async def save_context(self, user_id: int, context: List[Dict], ttl: int = 3600) -> bool:
        """
        Сохранить контекст разговора пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            context: Список сообщений в формате [{"role": "user/assistant", "content": "..."}]
            ttl: Время жизни контекста в секундах (по умолчанию 1 час)
            
        Returns:
            True если сохранение прошло успешно
        """
        try:
            redis = await self._get_redis_connection()
            
            # Сериализуем контекст в JSON
            context_json = json.dumps(context, ensure_ascii=False)
            
            # Сохраняем в Redis с TTL
            await redis.setex(f"context_{user_id}", ttl, context_json)
            
            await redis.aclose()
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения контекста для user {user_id}: {e}")
            return False
    
    async def get_context(self, user_id: int) -> List[Dict]:
        """
        Получить контекст разговора пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Список сообщений или пустой список если контекст не найден
        """
        try:
            redis = await self._get_redis_connection()
            
            # Получаем контекст из Redis
            context_json = await redis.get(f"context_{user_id}")
            
            await redis.aclose()
            
            if context_json:
                return json.loads(context_json)
            else:
                return []
                
        except Exception as e:
            print(f"Ошибка получения контекста для user {user_id}: {e}")
            return []
    
    async def add_message_to_context(self, user_id: int, role: str, content: str, max_messages: int = 30) -> bool:
        """
        Добавить сообщение в контекст разговора
        
        Args:
            user_id: ID пользователя в Telegram
            role: Роль отправителя ("user" или "assistant")
            content: Содержание сообщения
            max_messages: Максимальное количество сообщений в контексте
            
        Returns:
            True если добавление прошло успешно
        """
        try:
            # Получаем текущий контекст
            context = await self.get_context(user_id)
            
            # Добавляем новое сообщение
            new_message = {"role": role, "content": content}
            context.append(new_message)
            
            # Ограничиваем количество сообщений
            if len(context) > max_messages:
                context = context[-max_messages:]
            
            # Сохраняем обновленный контекст
            return await self.save_context(user_id, context)
            
        except Exception as e:
            print(f"Ошибка добавления сообщения в контекст для user {user_id}: {e}")
            return False
    
    async def clear_context(self, user_id: int) -> bool:
        """
        Очистить контекст разговора пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True если очистка прошла успешно
        """
        try:
            redis = await self._get_redis_connection()
            
            # Удаляем контекст из Redis
            await redis.delete(f"context_{user_id}")
            
            await redis.aclose()
            return True
            
        except Exception as e:
            print(f"Ошибка очистки контекста для user {user_id}: {e}")
            return False
    
    async def get_context_info(self, user_id: int) -> Dict:
        """
        Получить информацию о контексте пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Словарь с информацией о контексте
        """
        try:
            redis = await self._get_redis_connection()
            
            # Получаем TTL и размер контекста
            ttl = await redis.ttl(f"context_{user_id}")
            context = await self.get_context(user_id)
            
            await redis.aclose()
            
            return {
                "user_id": user_id,
                "messages_count": len(context),
                "ttl_seconds": ttl if ttl > 0 else 0,
                "has_context": len(context) > 0
            }
            
        except Exception as e:
            print(f"Ошибка получения информации о контексте для user {user_id}: {e}")
            return {
                "user_id": user_id,
                "messages_count": 0,
                "ttl_seconds": 0,
                "has_context": False
            }
    
    async def extend_context_ttl(self, user_id: int, ttl: int = 3600) -> bool:
        """
        Продлить время жизни контекста
        
        Args:
            user_id: ID пользователя в Telegram
            ttl: Новое время жизни в секундах
            
        Returns:
            True если продление прошло успешно
        """
        try:
            redis = await self._get_redis_connection()
            
            # Проверяем, существует ли контекст
            exists = await redis.exists(f"context_{user_id}")
            
            if exists:
                # Продлеваем TTL
                await redis.expire(f"context_{user_id}", ttl)
                await redis.aclose()
                return True
            else:
                await redis.aclose()
                return False
                
        except Exception as e:
            print(f"Ошибка продления TTL контекста для user {user_id}: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Проверить подключение к Redis
        
        Returns:
            True если подключение успешно
        """
        try:
            redis = await self._get_redis_connection()
            
            # Пробуем выполнить простую команду
            await redis.ping()
            
            await redis.aclose()
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к Redis: {e}")
            return False

# Создаем глобальный экземпляр сервиса
context_service = ContextService()


# Пример использования (для тестирования)
async def test_context_service():
    """Тест функций сервиса контекста"""
    print("Тестирование ContextService...")
    
    user_id = 123456
    
    # Тест 1: Добавление сообщений
    print("\n1. Добавление сообщений в контекст...")
    await context_service.add_message_to_context(user_id, "user", "Привет! Как дела?")
    await context_service.add_message_to_context(user_id, "assistant", "Привет! Отлично, спасибо! Как твои дела?")
    await context_service.add_message_to_context(user_id, "user", "Тоже хорошо! Можешь помочь с курсовой?")
    
    # Тест 2: Получение контекста
    print("\n2. Получение контекста...")
    context = await context_service.get_context(user_id)
    print(f"Контекст ({len(context)} сообщений):")
    for msg in context:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Тест 3: Информация о контексте
    print("\n3. Информация о контексте...")
    info = await context_service.get_context_info(user_id)
    print(f"Информация: {info}")
    
    # Тест 4: Очистка контекста
    print("\n4. Очистка контекста...")
    await context_service.clear_context(user_id)
    
    # Проверяем, что контекст очищен
    context_after_clear = await context_service.get_context(user_id)
    print(f"Контекст после очистки: {len(context_after_clear)} сообщений")
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    # Запуск тестов
    asyncio.run(test_context_service())