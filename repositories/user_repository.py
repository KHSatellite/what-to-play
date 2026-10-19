from uuid import UUID
from sqlalchemy.orm import Session
from models import User, UserSettings, PlatformAccount, LibraryEntry, Game
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_owner_by_library_entry_id(self, entry_id: UUID) -> User | None:
        return (
            self.db.query(User)
            .join(PlatformAccount, PlatformAccount.user_id == User.id)
            .join(LibraryEntry, LibraryEntry.platform_account_id == PlatformAccount.id)
            .filter(LibraryEntry.id == entry_id)
            .first()
        )

    def get_owners_by_game_title(self, title: str) -> list[User]:
        return (
            self.db.query(User)
            .join(PlatformAccount, PlatformAccount.user_id == User.id)
            .join(LibraryEntry, LibraryEntry.platform_account_id == PlatformAccount.id)
            .join(Game, Game.id == LibraryEntry.game_id)
            .filter(Game.title.ilike(f"%{title}%"))
            .distinct()
            .all()
        )


class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, db: Session):
        super().__init__(db, UserSettings)

    def get_by_user_id(self, user_id: UUID) -> UserSettings | None:
        return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
