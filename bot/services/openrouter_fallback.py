import os
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

MODELS = [
    "google/gemini-2.0-flash-lite-preview-02-05",
    "qwen/qwen-2.5-7b",
    "microsoft/phi-3-mini-128k",
    "mistralai/mistral-7b"
]

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.failure_counts = {m: 0 for m in MODELS}
    
    async def ask(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.api_key:
            return "❌ API ключ OpenRouter не найден. Проверь .env файл."
        
        for model in MODELS:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": max_tokens,
                            "temperature": 0.7
                        },
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.failure_counts[model] = 0
                            return data["choices"][0]["message"]["content"]
                        else:
                            logger.warning(f"Модель {model} вернула {resp.status}")
                            self.failure_counts[model] += 1
                            continue
            except Exception as e:
                logger.error(f"Ошибка с моделью {model}: {e}")
                self.failure_counts[model] += 1
                continue
        
        return "⚠️ Все модели временно недоступны. Попробуй позже."
