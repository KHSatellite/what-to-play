from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import PlatformAccount, LibraryEntry
from schemas import PlatformAccountCreate
from repositories.platform_account_repository import PlatformAccountRepository
from repositories.user_repository import UserRepository
from repositories.library_entry_repository import LibraryEntryRepository
from services.game_service import GameService
from services.platforms import CONNECTORS, MANUAL_PLATFORMS, get_connector
from services.platforms.base import extract_code, save_tokens, PlatformGame
from services import import_progress

LOOKUP_WORKERS = 6
MANUAL_USER_ID = "manual"


def _describe_http_error(e: Exception) -> str:
    resp = getattr(e, "response", None)
    if resp is not None:
        return f"HTTP {resp.status_code}: {resp.text[:160]}"
    return f"{type(e).__name__}: {e}"[:200]


class PlatformAccountService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PlatformAccountRepository(db)
        self.user_repository = UserRepository(db)
        self.library_entry_repository = LibraryEntryRepository(db)
        self.game_service = GameService(db)

    # ---------- hesap CRUD ----------

    def list_by_user(self, user_id: UUID) -> list[PlatformAccount]:
        return self.repository.get_by_user_id(user_id)

    def get_account(self, account_id: UUID) -> PlatformAccount:
        account = self.repository.get_by_id(account_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform hesabı bulunamadı")
        return account

    def create_account(self, payload: PlatformAccountCreate) -> PlatformAccount:
        self._ensure_user(payload.user_id)
        return self.repository.create(PlatformAccount(**payload.model_dump()))

    def delete_account(self, account_id: UUID) -> None:
        account = self.get_account(account_id)
        self.library_entry_repository.delete_by_platform_account_id(account_id)
        self.repository.delete(account)

    def _ensure_user(self, user_id: UUID) -> None:
        if self.user_repository.get_by_id(user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

    def _upsert_account(self, user_id: UUID, platform: str, platform_user_id: str, tokens: dict | None = None) -> PlatformAccount:
        account = self.repository.get_by_user_id_and_platform(user_id, platform)
        if account is None:
            account = PlatformAccount(user_id=user_id, platform_name=platform, platform_user_id=platform_user_id)
            self.db.add(account)
        account.platform_user_id = platform_user_id
        if tokens is not None:
            save_tokens(account, tokens)
        return self.repository.update(account)

    # ---------- bağlanma ----------

    def list_connectors(self, user_id: UUID) -> dict:
        connected = {a.platform_name: a for a in self.repository.get_by_user_id(user_id)}
        def _acc(a):
            return {"id": a.id, "platform_user_id": a.platform_user_id, "last_synced_at": a.last_synced_at} if a else None
        return {
            "connectors": [{**c.describe(), "account": _acc(connected.get(c.name))} for c in CONNECTORS.values()],
            "manual": [{"name": k, "label": v, "account": _acc(connected.get(k))} for k, v in MANUAL_PLATFORMS.items()],
        }

    def connect_steam_account(self, user_id: UUID, steam_id: str) -> PlatformAccount:
        self._ensure_user(user_id)
        return self._upsert_account(user_id, "steam", steam_id)

    def connect_with_code(self, user_id: UUID, platform: str, raw_code: str) -> PlatformAccount:
        connector = get_connector(platform)
        if connector is None or connector.mode != "code":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu platform kod ile bağlanmayı desteklemiyor")
        if "auth.gog.com/auth" in raw_code or "epicgames.com/id/login" in raw_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu, giriş sayfasının adresi. Giriş yaptıktan SONRA açılan sayfanın adresini (ya da gösterilen kodu) yapıştır.")
        code = extract_code(raw_code)
        if not code or len(code) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Kod ayıklanamadı (alınan: '{code[:20]}'). Adresin tamamını ya da sadece code= sonrasını yapıştır.")
        print(f"[connect:{platform}] kod uzunlugu={len(code)} ilk4={code[:4]}...")
        try:
            auth = connector.exchange_code(code)
        except Exception as e:
            detail = _describe_http_error(e)
            print(f"[connect:{platform}] kod dogrulanamadi: {detail}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{connector.label} kodu doğrulanamadı ({detail}). Kod tek kullanımlık ve kısa ömürlü: giriş sayfasını yeniden aç, yeni kodu hemen yapıştır.")
        return self._upsert_account(user_id, platform, auth.platform_user_id, auth.tokens)

    # ---------- manuel ekleme (giriş desteği olmayan platformlar) ----------

    def search_rawg(self, query: str) -> list[dict]:
        return [
            {"rawg_id": r["id"], "title": r["name"], "cover_image_url": r.get("background_image"), "released": r.get("released"), "estimated_hours": r.get("playtime") or 0}
            for r in self.game_service.rawg.search_games(query)
        ]

    def add_manual_game(self, user_id: UUID, platform: str, rawg_id: int) -> LibraryEntry:
        if platform not in MANUAL_PLATFORMS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz platform")
        self._ensure_user(user_id)
        account = self._upsert_account(user_id, platform, MANUAL_USER_ID)
        pgid = f"rawg:{rawg_id}"
        if pgid in self.library_entry_repository.get_platform_game_ids(account.id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu oyun zaten kütüphanende")
        try:
            result = self.game_service.rawg.get_game(rawg_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RAWG'da oyun bulunamadı")
        game, _ = self.game_service.upsert_from_rawg(result)
        return self.library_entry_repository.create(LibraryEntry(platform_account_id=account.id, game_id=game.id, platform_game_id=pgid))

    # ---------- kütüphane içe aktarma ----------

    def get_import_status(self, account_id: UUID) -> dict:
        return import_progress.get(account_id) or {"finished": True, "idle": True}

    def _lookup_safe(self, name: str) -> dict | None:
        try:
            return self.game_service.lookup_rawg(name)
        except Exception as e:
            print(f"[import] '{name}' RAWG aramasi basarisiz: {e}")
            return None

    def import_library(self, account_id: UUID) -> dict:
        account = self.get_account(account_id)
        connector = get_connector(account.platform_name)
        if connector is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu platform otomatik içe aktarmayı desteklemiyor")

        try:
            platform_games: list[PlatformGame] = connector.fetch_games(account)
            self.repository.update(account)  # yenilenen token'lar
        except Exception as e:
            self.db.rollback()
            import_progress.start(account_id, 0)
            detail = _describe_http_error(e)
            import_progress.finish(account_id, error=f"{connector.label} kütüphanesi alınamadı: {detail}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{connector.label} kütüphanesi alınamadı: {detail}")

        known = self.library_entry_repository.get_platform_game_ids(account_id)
        owned_game_ids = self.library_entry_repository.get_game_ids(account_id)
        pending = [g for g in platform_games if g.id not in known]
        import_progress.start(account_id, len(pending), platform_total=len(platform_games))
        imported = 0

        try:
            # 1) Ağ işi paralel: RAWG aramaları (DB'ye dokunmaz)
            with ThreadPoolExecutor(max_workers=LOOKUP_WORKERS) as pool:
                matches = list(pool.map(lambda g: self._lookup_safe(g.name), pending))

            # 2) DB işi sıralı
            for pg, match in zip(pending, matches):
                if match is None:
                    import_progress.step(account_id, imported=False, title=pg.name)
                    continue
                try:
                    game, _ = self.game_service.upsert_from_rawg(match)
                    if game.id in owned_game_ids:
                        # aynı platformda aynı oyuna ikinci kayıt (farklı sürüm/entitlement) — atla
                        import_progress.step(account_id, imported=False, duplicate=True)
                        continue
                    self.library_entry_repository.create(LibraryEntry(platform_account_id=account_id, game_id=game.id, platform_game_id=pg.id))
                    owned_game_ids.add(game.id)
                    imported += 1
                    import_progress.step(account_id, imported=True)
                except Exception as e:
                    self.db.rollback()
                    print(f"[import:{account.platform_name}] '{pg.name}' kaydedilirken hata: {e}")
                    import_progress.step(account_id, imported=False, title=pg.name)

            account = self.get_account(account_id)
            account.last_synced_at = datetime.utcnow()
            self.repository.update(account)
            import_progress.finish(account_id)
        except Exception as e:
            self.db.rollback()
            import_progress.finish(account_id, error=str(e))
            raise

        return {"imported": imported, "skipped": len(platform_games) - imported, "total": len(platform_games)}
