from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User, UserSettings
from schemas import UserCreate, UserUpdate, UserSettingsUpsert
from repositories.user_repository import UserRepository, UserSettingsRepository


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.settings_repository = UserSettingsRepository(db)

    def list_users(self) -> list[User]:
        return self.repository.get_all()

    def get_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        return user

    def create_user(self, payload: UserCreate) -> User:
        if self.repository.get_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı adı zaten kullanılıyor")
        if self.repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email zaten kullanılıyor")
        new_user = User(**payload.model_dump())
        return self.repository.create(new_user)

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.get_user(user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return self.repository.update(user)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.repository.delete(user)

    def get_settings(self, user_id: int) -> UserSettings:
        self.get_user(user_id)
        settings = self.settings_repository.get_by_user_id(user_id)
        if settings is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ayar bulunamadı")
        return settings

    def upsert_settings(self, user_id: int, payload: UserSettingsUpsert) -> UserSettings:
        self.get_user(user_id)
        settings = self.settings_repository.get_by_user_id(user_id)
        if settings is None:
            new_settings = UserSettings(user_id=user_id, **payload.model_dump())
            return self.settings_repository.create(new_settings)
        for field, value in payload.model_dump().items():
            setattr(settings, field, value)
        return self.settings_repository.update(settings)

    def get_owner_of_entry(self, entry_id: int) -> User:
        owner = self.repository.get_owner_by_library_entry_id(entry_id)
        if owner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu kütüphane kaydına ait kullanıcı bulunamadı")
        return owner

    def get_owners_by_game_title(self, title: str) -> list[User]:
        return self.repository.get_owners_by_game_title(title)
