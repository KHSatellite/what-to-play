from uuid import UUID
from sqlalchemy.orm import Session
from models import LibraryEntry
from repositories.base_repository import BaseRepository


class LibraryEntryRepository(BaseRepository[LibraryEntry]):
    def __init__(self, db: Session):
        super().__init__(db, LibraryEntry)

    def get_by_platform_account_id(self, platform_account_id: UUID) -> list[LibraryEntry]:
        return self.db.query(LibraryEntry).filter(LibraryEntry.platform_account_id == platform_account_id).all()

    def get_platform_game_ids(self, platform_account_id: UUID) -> set[str]:
        rows = (
            self.db.query(LibraryEntry.platform_game_id)
            .filter(LibraryEntry.platform_account_id == platform_account_id)
            .filter(LibraryEntry.platform_game_id.isnot(None))
            .all()
        )
        return {r[0] for r in rows}

    def get_game_ids(self, platform_account_id: UUID) -> set[UUID]:
        rows = self.db.query(LibraryEntry.game_id).filter(LibraryEntry.platform_account_id == platform_account_id).all()
        return {r[0] for r in rows}

    def delete_by_platform_account_id(self, platform_account_id: UUID) -> None:
        self.db.query(LibraryEntry).filter(LibraryEntry.platform_account_id == platform_account_id).delete()
        self.db.commit()
