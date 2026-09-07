from sqlalchemy.orm import Session
from models import LibraryEntry
from repositories.base_repository import BaseRepository


class LibraryEntryRepository(BaseRepository[LibraryEntry]):
    def __init__(self, db: Session):
        super().__init__(db, LibraryEntry)

    def get_by_platform_account_id(self, platform_account_id: int) -> list[LibraryEntry]:
        return self.db.query(LibraryEntry).filter(LibraryEntry.platform_account_id == platform_account_id).all()
