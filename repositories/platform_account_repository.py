from uuid import UUID
from sqlalchemy.orm import Session
from models import PlatformAccount
from repositories.base_repository import BaseRepository


class PlatformAccountRepository(BaseRepository[PlatformAccount]):
    def __init__(self, db: Session):
        super().__init__(db, PlatformAccount)

    def get_by_user_id(self, user_id: UUID) -> list[PlatformAccount]:
        return self.db.query(PlatformAccount).filter(PlatformAccount.user_id == user_id).all()

    def get_by_user_id_and_platform(self, user_id: UUID, platform_name: str) -> PlatformAccount | None:
        return (
            self.db.query(PlatformAccount)
            .filter(PlatformAccount.user_id == user_id)
            .filter(PlatformAccount.platform_name == platform_name)
            .first()
        )
