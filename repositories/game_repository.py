from uuid import UUID
from sqlalchemy.orm import Session
from models import Game, Category, LibraryEntry, PlatformAccount
from repositories.base_repository import BaseRepository


class GameRepository(BaseRepository[Game]):
    def __init__(self, db: Session):
        super().__init__(db, Game)

    def get_by_rawg_id(self, rawg_id: int) -> Game | None:
        return self.db.query(Game).filter(Game.rawg_id == rawg_id).first()

    def _user_library_query(self, user_id: UUID):
        return (
            self.db.query(Game)
            .join(LibraryEntry, LibraryEntry.game_id == Game.id)
            .join(PlatformAccount, PlatformAccount.id == LibraryEntry.platform_account_id)
            .filter(PlatformAccount.user_id == user_id)
        )

    def get_by_user_id(self, user_id: UUID, title: str | None = None) -> list[Game]:
        q = self._user_library_query(user_id)
        if title:
            q = q.filter(Game.title.ilike(f"%{title}%"))
        return q.all()

    def get_owned_rawg_ids(self, user_id: UUID) -> set[int]:
        rows = self._user_library_query(user_id).with_entities(Game.rawg_id).filter(Game.rawg_id.isnot(None)).all()
        return {r[0] for r in rows}

    def get_suggestions(
        self,
        user_id: UUID,
        category_id: UUID | None = None,
        min_hours: float | None = None,
        max_hours: float | None = None,
    ) -> list[tuple]:
        """(Game, platform_name, platform_game_id) satırları döner."""
        q = (
            self._user_library_query(user_id)
            .with_entities(Game, PlatformAccount.platform_name, LibraryEntry.platform_game_id)
            .filter(LibraryEntry.completed.is_(False))
        )
        if category_id is not None:
            q = q.filter(Game.categories.any(Category.id == category_id))
        if min_hours is not None:
            q = q.filter(Game.estimated_hours > min_hours)
        if max_hours is not None:
            q = q.filter(Game.estimated_hours <= max_hours)
        return q.all()

    def get_library_overview_for_user(self, user_id: UUID) -> list[tuple]:
        return (
            self.db.query(Game, PlatformAccount.platform_name, LibraryEntry.completed, LibraryEntry.id, LibraryEntry.platform_game_id)
            .join(LibraryEntry, LibraryEntry.game_id == Game.id)
            .join(PlatformAccount, PlatformAccount.id == LibraryEntry.platform_account_id)
            .filter(PlatformAccount.user_id == user_id)
            .order_by(Game.title)
            .all()
        )


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_by_names(self, names: list[str]) -> dict[str, Category]:
        if not names:
            return {}
        rows = self.db.query(Category).filter(Category.name.in_(names)).all()
        return {c.name: c for c in rows}
