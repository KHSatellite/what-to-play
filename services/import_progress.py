from threading import Lock
from uuid import UUID

_progress: dict[str, dict] = {}
_lock = Lock()


def start(account_id: UUID, total: int, platform_total: int = 0) -> None:
    with _lock:
        _progress[str(account_id)] = {
            "total": total, "platform_total": platform_total, "already": max(platform_total - total, 0),
            "done": 0, "imported": 0, "skipped": 0, "duplicates": 0, "finished": False, "skipped_titles": [],
        }


def step(account_id: UUID, imported: bool, title: str | None = None, duplicate: bool = False) -> None:
    with _lock:
        p = _progress.get(str(account_id))
        if p:
            p["done"] += 1
            if imported:
                p["imported"] += 1
            elif duplicate:
                p["duplicates"] += 1
            else:
                p["skipped"] += 1
                if title and len(p["skipped_titles"]) < 300:
                    p["skipped_titles"].append(title)


def finish(account_id: UUID, error: str | None = None) -> None:
    with _lock:
        p = _progress.get(str(account_id))
        if p:
            p["finished"] = True
            p["error"] = error


def get(account_id: UUID) -> dict | None:
    with _lock:
        p = _progress.get(str(account_id))
        return dict(p) if p else None
