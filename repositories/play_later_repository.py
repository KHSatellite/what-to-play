from uuid import UUID
from sqlalchemy.orm import Session
from models import PlayLater, Game, LibraryEntry, PlatformAccount
from repositories.base_repository import BaseRepository


class PlayLaterRepository(BaseRepository[PlayLater]):
    def __init__(self, db: Session):
        super().__init__(db, PlayLater)

    def list_for_user(self, user_id: UUID) -> list[PlayLater]:
        return self.db.query(PlayLater).filter(PlayLater.user_id == user_id).order_by(PlayLater.added_at.desc()).all()

    def get(self, user_id: UUID, game_id: UUID) -> PlayLater | None:
        return self.db.query(PlayLater).filter(PlayLater.user_id == user_id, PlayLater.game_id == game_id).first()

    def game_ids_for_user(self, user_id: UUID) -> set[UUID]:
        return {r[0] for r in self.db.query(PlayLater.game_id).filter(PlayLater.user_id == user_id).all()}

    def platforms_by_game(self, user_id: UUID) -> dict[UUID, list[tuple[str, str | None]]]:
        rows = (
            self.db.query(LibraryEntry.game_id, PlatformAccount.platform_name, LibraryEntry.platform_game_id)
            .join(PlatformAccount, PlatformAccount.id == LibraryEntry.platform_account_id)
            .filter(PlatformAccount.user_id == user_id)
            .all()
        )
        out: dict = {}
        for gid, platform, pgid in rows:
            out.setdefault(gid, []).append((platform, pgid))
        return out
