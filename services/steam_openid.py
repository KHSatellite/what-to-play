from urllib.parse import urlencode
import httpx

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
_TIMEOUT = 10.0


def build_login_redirect_url(return_to: str, realm: str) -> str:
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": realm,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{STEAM_OPENID_URL}?{urlencode(params)}"


def verify_and_extract_steam_id(query_params: dict) -> str | None:
    # Sadece openid.* parametrelerini Steam'e gönder; user_id gibi ekstralar hata çıkarabilir
    openid_params = {k: v for k, v in query_params.items() if k.startswith("openid.")}
    openid_params["openid.mode"] = "check_authentication"

    response = httpx.post(STEAM_OPENID_URL, data=openid_params, timeout=_TIMEOUT)
    response.raise_for_status()

    if "is_valid:true" not in response.text:
        return None

    claimed_id = query_params.get("openid.claimed_id", "")
    if "/openid/id/" not in claimed_id:
        return None
    return claimed_id.rsplit("/", 1)[-1]
