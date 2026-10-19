from uuid import UUID
from services.redis_client import redis_client

PERMISSION_TTL_SECONDS = 300


def cache_permission(user_id: UUID, permission_name: str) -> None:
    redis_client.set(f"perm:{user_id}:{permission_name}", "1", ex=PERMISSION_TTL_SECONDS)


def has_cached_permission(user_id: UUID, permission_name: str) -> bool:
    return redis_client.exists(f"perm:{user_id}:{permission_name}") == 1


def invalidate_user_permissions(user_id: UUID) -> None:
    for key in redis_client.scan_iter(f"perm:{user_id}:*"):
        redis_client.delete(key)
