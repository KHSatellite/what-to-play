from urllib.parse import quote
import httpx
from models import PlatformAccount
from services.platforms.base import PlatformConnector, PlatformGame, PlatformAuth, load_tokens, save_tokens

# GOG Galaxy istemcisinin herkese açık OAuth kimliği (Heroic / Lutris aynı değerleri kullanır)
CLIENT_ID = "46899977096215655"
CLIENT_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
REDIRECT_URI = "https://embed.gog.com/on_login_success?origin=client"
TOKEN_URL = "https://auth.gog.com/token"
PRODUCTS_URL = "https://embed.gog.com/account/getFilteredProducts"
LOGIN_URL = f"https://auth.gog.com/auth?client_id={CLIENT_ID}&redirect_uri={quote(REDIRECT_URI, safe='')}&response_type=code&layout=galaxy"
_TIMEOUT = 20.0
_UA = "GOGGalaxyClient/2.0.45.61 (GOG Galaxy)"


class GogConnector(PlatformConnector):
    name = "gog"
    label = "GOG"
    mode = "code"
    login_url = LOGIN_URL
    instructions = {
        "tr": "Açılan sekmede GOG'a giriş yap. Giriş bitince açılan sayfanın adres çubuğundaki adresi (embed.gog.com/on_login_success?...code=...) komple kopyalayıp buraya yapıştır. Kod tek kullanımlık, hemen yapıştır.",
        "en": "Sign in to GOG in the new tab. After login, copy the full address from the address bar (embed.gog.com/on_login_success?...code=...) and paste it here. The code is single-use, paste it right away.",
    }

    def _token(self, params: dict) -> dict:
        """GOG token servisi farklı istemcilerde farklı biçim bekleyebiliyor; sırayla dener."""
        creds = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
        headers = {"User-Agent": _UA, "Accept": "application/json"}
        attempts = [
            ("GET-query", lambda: httpx.get(TOKEN_URL, params={**creds, **params}, headers=headers, timeout=_TIMEOUT)),
            ("POST-form", lambda: httpx.post(TOKEN_URL, data={**creds, **params}, headers=headers, timeout=_TIMEOUT)),
            ("POST-basic", lambda: httpx.post(TOKEN_URL, data=params, auth=(CLIENT_ID, CLIENT_SECRET), headers=headers, timeout=_TIMEOUT)),
            ("GET-query-noUA", lambda: httpx.get(TOKEN_URL, params={**creds, **params}, timeout=_TIMEOUT)),
        ]
        last = None
        for name, call in attempts:
            r = call()
            if r.status_code == 200:
                print(f"[gog] token OK ({name})")
                return r.json()
            print(f"[gog] token hatasi ({name}) {r.status_code}: {r.text[:200]}")
            last = r
            if "invalid_grant" in r.text or "invalid_code" in r.text.lower():
                break  # kod geçersiz/süresi dolmuş; başka biçim denemenin anlamı yok
        last.raise_for_status()
        return last.json()

    def exchange_code(self, code: str) -> PlatformAuth:
        t = self._token({"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI})
        return PlatformAuth(platform_user_id=str(t["user_id"]), tokens={"access": t["access_token"], "refresh": t["refresh_token"]})

    def _refresh(self, account: PlatformAccount) -> str:
        tokens = load_tokens(account)
        if not tokens.get("refresh"):
            raise RuntimeError("GOG oturumu yok, yeniden bağlan")
        t = self._token({"grant_type": "refresh_token", "refresh_token": tokens["refresh"]})
        save_tokens(account, {**tokens, "access": t["access_token"], "refresh": t["refresh_token"]})
        return t["access_token"]

    def fetch_games(self, account: PlatformAccount) -> list[PlatformGame]:
        token = self._refresh(account)
        games, page = [], 1
        with httpx.Client(headers={"Authorization": f"Bearer {token}", "User-Agent": _UA}, timeout=_TIMEOUT) as c:
            while True:
                r = c.get(PRODUCTS_URL, params={"mediaType": 1, "page": page})
                r.raise_for_status()
                data = r.json()
                games += [PlatformGame(id=str(p["id"]), name=p["title"]) for p in data.get("products", []) if not p.get("isDLC")]
                if page >= int(data.get("totalPages") or 1):
                    break
                page += 1
        return games
