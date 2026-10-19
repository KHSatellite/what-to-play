import json
import re
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from models import PlatformAccount


@dataclass
class PlatformGame:
    id: str
    name: str


@dataclass
class PlatformAuth:
    platform_user_id: str
    tokens: dict | None = None


class PlatformConnector:
    """Her platform için tek sınıf: nasıl bağlanılır (redirect ya da yetki kodu) ve kütüphane nasıl çekilir."""

    name: str = ""
    label: str = ""
    mode: str = "code"  # 'redirect' | 'code'
    login_url: str | None = None
    instructions: dict = {"tr": "", "en": ""}

    def exchange_code(self, code: str) -> PlatformAuth:
        raise NotImplementedError

    def fetch_games(self, account: PlatformAccount) -> list[PlatformGame]:
        raise NotImplementedError

    def describe(self) -> dict:
        return {"name": self.name, "label": self.label, "mode": self.mode, "login_url": self.login_url, "instructions": self.instructions}


def load_tokens(account: PlatformAccount) -> dict:
    try:
        return json.loads(account.access_token) if account.access_token else {}
    except ValueError:
        return {}


def save_tokens(account: PlatformAccount, tokens: dict) -> None:
    account.access_token = json.dumps(tokens)


def extract_code(raw: str, key: str = "code") -> str:
    """Kullanıcı ham kodu, URL'yi ya da JSON'u yapıştırabilir; hepsinden kodu çıkarır."""
    raw = raw.strip()
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            for k in ("authorizationCode", "code", key):
                if data.get(k):
                    return str(data[k])
        except ValueError:
            pass
    if raw.startswith("http"):
        qs = parse_qs(urlparse(raw).query)
        for k in (key, "code"):
            if qs.get(k):
                return qs[k][0]
    m = re.search(r'"?(?:authorizationCode|code)"?\s*[:=]\s*"?([A-Za-z0-9_\-]+)', raw)
    if m:
        return m.group(1)
    return raw.strip('"\' ')
