from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import PlatformAccount
from schemas import PlatformAccountCreate
from repositories.platform_account_repository import PlatformAccountRepository
from repositories.user_repository import UserRepository


class PlatformAccountService:
    def __init__(self, db: Session):
        self.repository = PlatformAccountRepository(db)
        self.user_repository = UserRepository(db)

    def list_by_user(self, user_id: int) -> list[PlatformAccount]:
        return self.repository.get_by_user_id(user_id)

    def get_account(self, account_id: int) -> PlatformAccount:
        account = self.repository.get_by_id(account_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform hesabı bulunamadı")
        return account

    def create_account(self, payload: PlatformAccountCreate) -> PlatformAccount:
        if self.user_repository.get_by_id(payload.user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        new_account = PlatformAccount(**payload.model_dump())
        return self.repository.create(new_account)

    def delete_account(self, account_id: int) -> None:
        account = self.get_account(account_id)
        self.repository.delete(account)
