import pytest
from unittest.mock import AsyncMock, patch
from bot.services.openrouter_fallback import OpenRouterClient

@pytest.mark.asyncio
async def test_openrouter_fallback():
    client = OpenRouterClient()
    client.api_key = "test_key"
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "тестовый ответ"}}]})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await client.ask("тест")
        assert result == "тестовый ответ"
