from services.platforms.steam import SteamConnector
from services.platforms.epic import EpicConnector
from services.platforms.gog import GogConnector

CONNECTORS = {c.name: c for c in (SteamConnector(), EpicConnector(), GogConnector())}

# Giriş desteği olmayan platformlar: oyunlar RAWG aramasıyla tek tek eklenir
MANUAL_PLATFORMS = {
    "ubisoft": "Ubisoft Connect",
    "ea": "EA App",
    "rockstar": "Rockstar Games",
    "battlenet": "Battle.net",
    "xbox": "Xbox / Game Pass",
    "playstation": "PlayStation",
    "nintendo": "Nintendo",
    "other": "Diğer",
}


def get_connector(platform: str):
    return CONNECTORS.get(platform)
