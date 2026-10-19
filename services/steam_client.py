import httpx
from config import settings

STEAM_API_BASE = "https://api.steampowered.com"
_TIMEOUT = 15.0


def get_owned_games(steam_id: str) -> list[dict]:
    r = httpx.get(
        f"{STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/",
        params={
            "key": settings.steam_api_key,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": 1,
            "include_played_free_games": 1,
        },
        timeout=_TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("response", {}).get("games", [])
