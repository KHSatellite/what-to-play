from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import LibraryEntry
from schemas import LibraryEntryCreate, LibraryEntryUpdate
from repositories.library_entry_repository import LibraryEntryRepository
from repositories.platform_account_repository import PlatformAccountRepository
from repositories.game_repository import GameRepository


class LibraryEntryService:
    def __init__(self, db: Session):
        self.repository = LibraryEntryRepository(db)
        self.platform_account_repository = PlatformAccountRepository(db)
        self.game_repository = GameRepository(db)

    def list_by_platform_account(self, platform_account_id: int) -> list[LibraryEntry]:
        return self.repository.get_by_platform_account_id(platform_account_id)

    def get_entry(self, entry_id: int) -> LibraryEntry:
        entry = self.repository.get_by_id(entry_id)
        if entry is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kütüphane kaydı bulunamadı")
        return entry

    def create_entry(self, payload: LibraryEntryCreate) -> LibraryEntry:
        if self.platform_account_repository.get_by_id(payload.platform_account_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform hesabı bulunamadı")
        if self.game_repository.get_by_id(payload.game_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oyun bulunamadı")
        new_entry = LibraryEntry(**payload.model_dump())
        return self.repository.create(new_entry)

    def update_entry(self, entry_id: int, payload: LibraryEntryUpdate) -> LibraryEntry:
        entry = self.get_entry(entry_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(entry, field, value)
        return self.repository.update(entry)

    def delete_entry(self, entry_id: int) -> None:
        entry = self.get_entry(entry_id)
        self.repository.delete(entry)
