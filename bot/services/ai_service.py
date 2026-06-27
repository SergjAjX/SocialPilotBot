import aiohttp
import asyncio
from config import OPENROUTER_API_KEY

class AIService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=60)
    
    async def generate_ideas(self, topic: str) -> str:
        prompt = f"""Ты творческий эксперт по SMM. Генерируй 5 идей для постов по теме: '{topic}'

Для каждой идеи укажи:
1. Цепляющий заголовок
2. Формат поста (Reels, Carousel, Poll, Story)
3. Краткое описание
4. Лучшая платформа (Instagram, TikTok, Telegram, YouTube)

Формат ответа:
1️⃣ [Заголовок] ([Формат])
[Описание]
📱 Лучше для: [Платформа]

Ответь на русском языке."""
        
        return await self._call_api(prompt)
    
    async def optimize_text(self, text: str, platform: str) -> str:
        platform_tips = {
            "telegram": "Напиши длинно, информативно, добавь эмодзи и хештеги",
            "instagram": "Сделай увлекательно, добавь CTA, используй релевантные хештеги",
            "tiktok": "Коротко, цепляюще, используй тренды и эмодзи",
            "vk": "Добавь личность, используй VK-стиль, релевантные хештеги",
            "youtube": "Сделай привлекательно, первые строки критичны, добавь временные метки"
        }
        
        tips = platform_tips.get(platform.lower(), "")
        
        prompt = f"""Ты SMM эксперт. Оптимизируй текст для {platform}.

{tips}

Исходный текст:
{text}

Предоставь:
1. Оптимизированный текст
2. 5 релевантных хештегов
3. Лучшее время для публикации (если применимо)

Ответ на русском языке."""
        
        return await self._call_api(prompt)
    
    async def analyze_post(self, post_content: str) -> str:
        prompt = f"""Ты аналитик SMM. Проанализируй этот пост:

{post_content}

Дай анализ в формате:
1. Тон: [нейтральный/позитивный/негативный/смешной/мотивирующий]
2. Целевая аудитория: [описание]
3. Сильные стороны: [список]
4. Слабые стороны: [список]
5. Похожие идеи для своего поста (2): [идеи]

Ответ на русском языке."""
        
        return await self._call_api(prompt)
    
    async def _call_api(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "google/gemma-2-9b-it:free",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error = await response.text()
                        return f"Ошибка: {response.status}"
        
        except asyncio.TimeoutError:
            return "Запрос истек по времени. Попробуй снова."
        except Exception as e:
            return f"Ошибка: {str(e)}"

ai_service = AIService()
