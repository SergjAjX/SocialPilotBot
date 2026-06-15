import pytest
from bot.services.cache import Cache
import hashlib

def test_cache_set_get(tmp_path):
    cache = Cache(cache_dir=tmp_path)
    prompt = "привет"
    response = "мир"
    cache.set(prompt, response)
    assert cache.get(prompt) == response

def test_cache_miss(tmp_path):
    cache = Cache(cache_dir=tmp_path)
    assert cache.get("неизвестно") is None
