import httpx
from models import PlatformAccount
from services.platforms.base import PlatformConnector, PlatformGame, PlatformAuth, load_tokens, save_tokens

# Legendary / Heroic'in kullandığı herkese açık launcher istemcisi
CLIENT_ID = "34a02cf8f4414e29b15921876da36f9a"
CLIENT_SECRET = "daafbccc737745039dffe53d94fc76cf"
OAUTH_URL = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
ASSETS_URL = "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/public/assets/Windows"
CATALOG_URL = "https://catalog-public-service-prod06.ol.epicgames.com/catalog/api/shared/namespace/{ns}/bulk/items"
LOGIN_URL = (
    "https://www.epicgames.com/id/login?redirectUrl="
    "https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3D34a02cf8f4414e29b15921876da36f9a%26responseType%3Dcode"
)
_TIMEOUT = 25.0
_UA = "UELauncher/11.0.1-14907503+++Portal+Release-Live Windows/10.0.19041.1.256.64bit"
_EXCLUDED_CATEGORIES = {"addons", "digitalextras", "software", "assets", "plugins", "applications"}


class EpicConnector(PlatformConnector):
    name = "epic"
    label = "Epic Games"
    mode = "code"
    login_url = LOGIN_URL
    instructions = {
        "tr": 'Açılan sekmede Epic hesabına giriş yap. Ekranda "authorizationCode" içeren bir metin görünecek; o kodu (ya da tüm metni) buraya yapıştır.',
        "en": 'Sign in to Epic in the new tab. You will see text containing "authorizationCode"; paste that code (or the whole text) here.',
    }

    def _token(self, data: dict) -> dict:
        r = httpx.post(OAUTH_URL, data={**data, "token_type": "eg1"}, auth=(CLIENT_ID, CLIENT_SECRET), headers={"User-Agent": _UA}, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def exchange_code(self, code: str) -> PlatformAuth:
        t = self._token({"grant_type": "authorization_code", "code": code})
        return PlatformAuth(platform_user_id=t["account_id"], tokens={"access": t["access_token"], "refresh": t["refresh_token"], "display_name": t.get("displayName")})

    def _refresh(self, account: PlatformAccount) -> str:
        tokens = load_tokens(account)
        if not tokens.get("refresh"):
            raise RuntimeError("Epic oturumu yok, yeniden bağlan")
        t = self._token({"grant_type": "refresh_token", "refresh_token": tokens["refresh"]})
        save_tokens(account, {**tokens, "access": t["access_token"], "refresh": t["refresh_token"]})
        return t["access_token"]

    @staticmethod
    def _is_base_game(item: dict) -> bool:
        paths = {c.get("path", "") for c in item.get("categories", [])}
        if "games" not in paths or item.get("mainGameItem"):
            return False
        return not any(p.split("/")[0] in _EXCLUDED_CATEGORIES or p in _EXCLUDED_CATEGORIES for p in paths)

    def fetch_games(self, account: PlatformAccount) -> list[PlatformGame]:
        token = self._refresh(account)
        headers = {"Authorization": f"Bearer {token}", "User-Agent": _UA}
        with httpx.Client(headers=headers, timeout=_TIMEOUT) as c:
            # Sadece yüklenebilir oyun varlıkları (DLC/Unreal varlıkları burada yok)
            r = c.get(ASSETS_URL, params={"label": "Live"})
            r.raise_for_status()
            by_ns: dict[str, dict[str, str]] = {}
            for a in r.json():
                ns, item_id, app = a.get("namespace"), a.get("catalogItemId"), a.get("appName")
                if ns and item_id and ns != "ue":
                    by_ns.setdefault(ns, {})[item_id] = app

            games, seen_titles = [], set()
            for ns, items in by_ns.items():
                ids = list(items)
                for i in range(0, len(ids), 50):
                    params = [("id", x) for x in ids[i:i + 50]] + [("includeDLCDetails", "false"), ("includeMainGameDetails", "false"), ("country", "US"), ("locale", "en")]
                    r = c.get(CATALOG_URL.format(ns=ns), params=params)
                    if r.status_code != 200:
                        continue
                    for item_id, item in r.json().items():
                        if not self._is_base_game(item):
                            continue
                        title = (item.get("title") or "").strip()
                        if not title or title.lower() in seen_titles:
                            continue
                        seen_titles.add(title.lower())
                        games.append(PlatformGame(id=f"{ns}:{item_id}", name=title))
        return games
