from sqlalchemy.orm import Session
from models import Game, Category, LibraryEntry, PlatformAccount
from repositories.base_repository import BaseRepository


class GameRepository(BaseRepository[Game]):
    def __init__(self, db: Session):
        super().__init__(db, Game)

    def get_by_rawg_id(self, rawg_id: int) -> Game | None:
        return self.db.query(Game).filter(Game.rawg_id == rawg_id).first()

    def get_by_user_id(self, user_id: int, title: str | None = None) -> list[Game]:
        query = (
            self.db.query(Game)
            .join(LibraryEntry, LibraryEntry.game_id == Game.id)
            .join(PlatformAccount, PlatformAccount.id == LibraryEntry.platform_account_id)
            .filter(PlatformAccount.user_id == user_id)
        )
        if title:
            query = query.filter(Game.title.ilike(f"%{title}%"))
        return query.all()


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()
