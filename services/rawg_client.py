import time
import httpx
from config import settings

RAWG_BASE_URL = "https://api.rawg.io/api"
_TIMEOUT = httpx.Timeout(12.0, connect=6.0)
_RETRIES = 3

_client = httpx.Client(base_url=RAWG_BASE_URL, timeout=_TIMEOUT, limits=httpx.Limits(max_connections=10))


class RawgClient:
    def __init__(self):
        self.api_key = settings.rawg_api_key

    def _get(self, path: str, **params) -> dict:
        params["key"] = self.api_key
        last_err = None
        for attempt in range(_RETRIES):
            try:
                r = _client.get(path, params=params)
                if r.status_code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                r.raise_for_status()
                return r.json()
            except (httpx.TimeoutException, httpx.TransportError) as e:
                last_err = e
                time.sleep(0.5 * (attempt + 1))
        raise last_err or RuntimeError("RAWG istegi basarisiz")

    def get_genres(self) -> list[dict]:
        return self._get("/genres")["results"]

    def search_games(self, query: str, exact: bool = False) -> list[dict]:
        params = {"search": query, "page_size": 5}
        if exact:
            params["search_exact"] = "true"
        return self._get("/games", **params)["results"]

    def get_games(self, genre_rawg_id: int | None = None, page_size: int = 40, page: int = 1) -> list[dict]:
        params = {"page_size": page_size, "page": page, "ordering": "-rating", "metacritic": "60,100"}
        if genre_rawg_id is not None:
            params["genres"] = genre_rawg_id
        return self._get("/games", **params)["results"]

    def get_game(self, rawg_id: int) -> dict:
        return self._get(f"/games/{rawg_id}")

    def get_popular(self, page_size: int = 24) -> list[dict]:
        return self._get("/games", page_size=page_size, ordering="-added")["results"]
