from models import PlatformAccount
from services.platforms.base import PlatformConnector, PlatformGame
from services.steam_client import get_owned_games


class SteamConnector(PlatformConnector):
    name = "steam"
    label = "Steam"
    mode = "redirect"
    instructions = {"tr": "Steam ile giriş yap; siteye otomatik geri dönersin.", "en": "Sign in with Steam; you are redirected back automatically."}

    def fetch_games(self, account: PlatformAccount) -> list[PlatformGame]:
        return [PlatformGame(id=str(g["appid"]), name=g["name"]) for g in get_owned_games(account.platform_user_id)]
