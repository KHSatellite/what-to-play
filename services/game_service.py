import random
import re
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Game
from schemas import GameCreate, GameUpdate
from repositories.game_repository import GameRepository, CategoryRepository
from repositories.user_repository import UserRepository, UserSettingsRepository
from services.rawg_client import RawgClient
from services.memory_cache import cache_get, cache_set

DEFAULT_SHORT_MAX_HOURS = 5.0
DEFAULT_MEDIUM_MAX_HOURS = 15.0
SUGGESTION_COUNT = 20


_EDITION_RE = re.compile(
    r"\s*[-:(]?\s*\b(game of the year|goty|definitive|deluxe|ultimate|complete|gold|premium|standard|enhanced|"
    r"anniversary|special|collector'?s|digital|legendary|royal|director'?s cut|the)?\s*edition\b\)?\s*$",
    re.IGNORECASE,
)


def _normalize_title(title: str) -> str:
    cleaned = title.replace("\u2122", "").replace("\u00ae", "").replace("\u2019", "'")
    cleaned = cleaned.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def _strip_edition(title: str) -> str:
    return _EDITION_RE.sub("", _normalize_title(title)).strip(" -:")


def _is_edition_variant(shorter: str, longer: str) -> bool:
    if not longer.startswith(shorter):
        return False
    rest = longer[len(shorter):].lstrip()
    return rest[:1] in (":", "-", "(")


def _titles_match(a: str, b: str) -> bool:
    a, b = _normalize_title(a), _normalize_title(b)
    if a == b or _strip_edition(a) == _strip_edition(b):
        return True
    return _is_edition_variant(a, b) if len(a) <= len(b) else _is_edition_variant(b, a)


def _rawg_to_dto(item: dict) -> dict:
    return {
        "id": None,
        "title": item["name"],
        "estimated_hours": item.get("playtime") or 0,
        "cover_image_url": item.get("background_image"),
        "source": "rawg",
        "link": f"https://rawg.io/games/{item['slug']}" if item.get("slug") else None,
        "rawg_id": item["id"],
    }


class GameService:
    def __init__(self, db: Session, rawg: RawgClient | None = None):
        self.repository = GameRepository(db)
        self.category_repository = CategoryRepository(db)
        self.user_repository = UserRepository(db)
        self.rawg = rawg or RawgClient()

    def list_games(self) -> list[Game]:
        return self.repository.get_all()

    def get_game(self, game_id: UUID) -> Game:
        game = self.repository.get_by_id(game_id)
        if game is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oyun bulunamadı")
        return game

    def create_game(self, payload: GameCreate) -> Game:
        if payload.rawg_id is not None and self.repository.get_by_rawg_id(payload.rawg_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu rawg_id zaten kayıtlı")
        return self.repository.create(Game(**payload.model_dump()))

    def update_game(self, game_id: UUID, payload: GameUpdate) -> Game:
        game = self.get_game(game_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(game, field, value)
        return self.repository.update(game)

    def delete_game(self, game_id: UUID) -> None:
        self.repository.delete(self.get_game(game_id))

    def add_category(self, game_id: UUID, category_id: UUID) -> Game:
        game = self.get_game(game_id)
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı")
        if category not in game.categories:
            game.categories.append(category)
            self.repository.update(game)
        return game

    def remove_category(self, game_id: UUID, category_id: UUID) -> Game:
        game = self.get_game(game_id)
        category = self.category_repository.get_by_id(category_id)
        if category in game.categories:
            game.categories.remove(category)
            self.repository.update(game)
        return game

    def list_by_user(self, user_id: UUID, title: str | None = None) -> list[Game]:
        if self.user_repository.get_by_id(user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        return self.repository.get_by_user_id(user_id, title)

    def lookup_rawg(self, title: str) -> dict | None:
        """Sadece ağ: RAWG'da en iyi eşleşmeyi bulur. DB'ye dokunmaz, thread'de çalışabilir."""
        queries = [title]
        stripped = _strip_edition(title)
        if stripped and stripped.lower() != title.lower():
            queries.append(stripped)
        for q in queries:
            exact = self.rawg.search_games(q, exact=True)
            if exact:
                return exact[0]
            for cand in self.rawg.search_games(q)[:5]:
                if _titles_match(q, cand["name"]):
                    return cand
        return None

    def upsert_from_rawg(self, result: dict) -> tuple[Game, bool]:
        """Sadece DB: RAWG sonucunu oyuna çevirir, kategorilerini bağlar."""
        existing = self.repository.get_by_rawg_id(result["id"])
        if existing:
            return existing, False
        game = Game(
            title=result["name"],
            rawg_id=result["id"],
            rawg_slug=result.get("slug"),
            estimated_hours=result.get("playtime") or 8,
            cover_image_url=result.get("background_image"),
        )
        names = [g["name"] for g in result.get("genres", [])]
        game.categories = list(self.category_repository.get_by_names(names).values())
        return self.repository.create(game), True

    def create_from_rawg(self, title: str) -> Game:
        result = self.lookup_rawg(title)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RAWG'da bu isimde bir oyun bulunamadı")
        game, created = self.upsert_from_rawg(result)
        if not created:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu oyun zaten kayıtlı")
        return game


class SuggestionService:
    def __init__(self, db: Session, rawg: RawgClient | None = None):
        self.repository = GameRepository(db)
        self.category_repository = CategoryRepository(db)
        self.user_repository = UserRepository(db)
        self.settings_repository = UserSettingsRepository(db)
        self.rawg = rawg or RawgClient()

    def _ensure_user(self, user_id: UUID) -> None:
        if self.user_repository.get_by_id(user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

    def _duration_range(self, user_id: UUID, duration: str | None) -> tuple[float | None, float | None]:
        s = self.settings_repository.get_by_user_id(user_id)
        short_max = s.short_max_hours if s else DEFAULT_SHORT_MAX_HOURS
        medium_max = s.medium_max_hours if s else DEFAULT_MEDIUM_MAX_HOURS
        ranges = {None: (None, None), "short": (None, short_max), "medium": (short_max, medium_max), "long": (medium_max, None)}
        if duration not in ranges:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="duration 'short', 'medium' ya da 'long' olmalı")
        return ranges[duration]

    @staticmethod
    def _in_range(hours: float, lo: float | None, hi: float | None) -> bool:
        return (lo is None or hours > lo) and (hi is None or hours <= hi)

    @staticmethod
    def _library_link(game: Game, platform: str, platform_game_id: str | None) -> str | None:
        if platform == "steam" and platform_game_id:
            return f"https://store.steampowered.com/app/{platform_game_id}"
        return f"https://rawg.io/games/{game.rawg_slug}" if game.rawg_slug else None

    def _game_to_dto(self, g: Game, platforms: list[str], platform_game_id: str | None) -> dict:
        return {
            "id": g.id,
            "title": g.title,
            "estimated_hours": g.estimated_hours,
            "cover_image_url": g.cover_image_url,
            "source": "library",
            "platform": platforms[0],
            "platforms": platforms,
            "link": self._library_link(g, platforms[0], platform_game_id),
            "rawg_id": g.rawg_id,
        }

    def _library_rows(self, user_id: UUID, category_id: UUID | None, duration: str | None) -> list[tuple]:
        """Oyun bazında gruplar: (Game, [platformlar], ilk platform_game_id). Steam varsa link için öne alınır."""
        self._ensure_user(user_id)
        lo, hi = self._duration_range(user_id, duration)
        grouped: dict = {}
        for g, platform, pgid in self.repository.get_suggestions(user_id, category_id, lo, hi):
            entry = grouped.setdefault(g.id, [g, [], None])
            if platform not in entry[1]:
                entry[1].append(platform)
            if platform == "steam" or entry[2] is None:
                entry[2] = pgid
                if platform == "steam":
                    entry[1].remove("steam"); entry[1].insert(0, "steam")
        return [tuple(v) for v in grouped.values()]

    @staticmethod
    def _allocate(available: dict[str, int], total: int) -> dict[str, int]:
        """Sabit kota: Steam %50, RAWG %25, diğer kütüphane platformları kalan %25'i paylaşır
        (steam+epic+rawg → 10/5/5; +gog → 10/3/2/5). Bir kaynakta yeterli oyun yoksa açık önce
        diğer kütüphane platformlarına, en son RAWG'a geçer."""
        lib = [k for k in available if k != "rawg"]
        target: dict[str, int] = {}
        if lib:
            rawg_q = total // 4 if "rawg" in available else 0
            lib_q = total - rawg_q
            if "steam" in lib:
                target["steam"] = total // 2
                others = [k for k in lib if k != "steam"]
                for i, k in enumerate(others):
                    target[k] = (lib_q - target["steam"]) // len(others) + (1 if i < (lib_q - target["steam"]) % len(others) else 0)
            else:
                for i, k in enumerate(lib):
                    target[k] = lib_q // len(lib) + (1 if i < lib_q % len(lib) else 0)
            if "rawg" in available:
                target["rawg"] = rawg_q
        else:
            target = {"rawg": total} if "rawg" in available else {}

        alloc = {k: min(target.get(k, 0), available[k]) for k in available}
        # açığı sırayla kapat: önce Steam, sonra diğer kütüphane platformları, en son RAWG
        order = [k for k in ["steam"] + [x for x in lib if x != "steam"] if k in alloc] + (["rawg"] if "rawg" in alloc else [])
        for k in order:
            while alloc[k] < available[k] and sum(alloc.values()) < total:
                alloc[k] += 1
        return alloc

    def get_suggestions(self, user_id: UUID, category_id: UUID | None, duration: str | None) -> list[Game]:
        return [g for g, _, _ in self._library_rows(user_id, category_id, duration)]

    def get_random_suggestion(self, user_id: UUID, category_id: UUID | None, duration: str | None) -> dict:
        rows = self._library_rows(user_id, category_id, duration)
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu kriterlere uyan oyun bulunamadı")
        return self._game_to_dto(*random.choice(rows))

    def _rawg_fill(self, user_id: UUID, category_id: UUID | None, lo, hi, needed: int) -> list[dict]:
        genre_id = None
        if category_id is not None:
            cat = self.category_repository.get_by_id(category_id)
            if cat is None or cat.rawg_id is None:
                return []
            genre_id = cat.rawg_id
        owned = self.repository.get_owned_rawg_ids(user_id)
        out, page = [], 1
        while len(out) < needed and page <= 3:
            try:
                items = self.rawg.get_games(genre_id, page_size=40, page=page)
            except Exception as e:
                print(f"[suggest] RAWG hatasi: {e}")
                break
            if not items:
                break
            for it in items:
                if it["id"] in owned:
                    continue
                if not self._in_range(it.get("playtime") or 0, lo, hi):
                    continue
                out.append(_rawg_to_dto(it))
            page += 1
        random.shuffle(out)
        return out[:needed]

    def get_combined_suggestions(self, user_id: UUID, category_id: UUID | None, duration: str | None) -> list[dict]:
        rows = self._library_rows(user_id, category_id, duration)
        random.shuffle(rows)
        # Her oyun ilk platformunun kovasına girer; RAWG ayrı bir kova
        buckets: dict[str, list] = {}
        for r in rows:
            buckets.setdefault(r[1][0], []).append(r)
        available = {k: len(v) for k, v in buckets.items()}
        available["rawg"] = SUGGESTION_COUNT
        alloc = self._allocate(available, SUGGESTION_COUNT)

        lo, hi = self._duration_range(user_id, duration)
        rawg_items = self._rawg_fill(user_id, category_id, lo, hi, alloc["rawg"]) if alloc["rawg"] else []
        if len(rawg_items) < alloc["rawg"]:
            available["rawg"] = len(rawg_items)
            alloc = self._allocate(available, SUGGESTION_COUNT)

        picks = []
        for k, n in alloc.items():
            if k != "rawg":
                picks += [self._game_to_dto(*r) for r in buckets[k][:n]]
        picks += rawg_items[:alloc["rawg"]]
        random.shuffle(picks)
        return picks

    def get_library_overview(self, user_id: UUID) -> list[dict]:
        """Aynı oyun birden fazla platformda varsa tek kart, platform listesiyle."""
        self._ensure_user(user_id)
        grouped: dict = {}
        for g, platform, completed, entry_id, pgid in self.repository.get_library_overview_for_user(user_id):
            item = grouped.get(g.id)
            if item is None:
                item = grouped[g.id] = {
                    "game_id": g.id,
                    "title": g.title,
                    "estimated_hours": g.estimated_hours,
                    "cover_image_url": g.cover_image_url,
                    "categories": [c.name for c in g.categories],
                    "entries": [],
                    "link": None,
                }
            item["entries"].append({"entry_id": entry_id, "platform_name": platform, "completed": completed})
            if platform == "steam" or item["link"] is None:
                item["link"] = self._library_link(g, platform, pgid)
        out = []
        for item in grouped.values():
            # aynı platformdan birden fazla kayıt (ör. iki Epic katalog öğesi aynı oyuna eşleşti) tek rozet
            item["platforms"] = sorted({e["platform_name"] for e in item["entries"]}, key=lambda p: (p != "steam", p))
            item["completed"] = all(e["completed"] for e in item["entries"])
            out.append(item)
        return out

    def get_showcase(self) -> dict:
        cached = cache_get("public:showcase")
        if cached is not None:
            return cached
        try:
            games = [_rawg_to_dto(it) for it in self.rawg.get_popular(24)]
        except Exception as e:
            print(f"[showcase] RAWG hatasi: {e}")
            games = []
        data = {
            "games": games,
            "stats": {
                "games": self.repository.count(),
                "categories": self.category_repository.count(),
                "users": self.user_repository.count(),
            },
        }
        cache_set("public:showcase", data)
        return data
