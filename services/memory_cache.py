from cachetools import TTLCache

_cache: TTLCache = TTLCache(maxsize=256, ttl=300)


def cache_get(key: str):
    return _cache.get(key)


def cache_set(key: str, value) -> None:
    _cache[key] = value


def cache_delete(key: str) -> None:
    _cache.pop(key, None)
