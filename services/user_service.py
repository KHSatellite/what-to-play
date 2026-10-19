from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User, UserSettings
from schemas import UserCreate, UserUpdate, UserSettingsUpsert
from repositories.user_repository import UserRepository, UserSettingsRepository
from services.password_service import hash_password
from services.localization_service import translate
from services.email_queue import publish_welcome_email


class UserService:
    def __init__(self, db: Session, locale: str = "en"):
        self.repository = UserRepository(db)
        self.settings_repository = UserSettingsRepository(db)
        self.locale = locale

    def list_users(self) -> list[User]:
        return self.repository.get_all()

    def get_user(self, user_id: UUID) -> User:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("user_not_found", self.locale))
        return user

    def create_user(self, payload: UserCreate) -> User:
        if self.repository.get_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=translate("username_taken", self.locale))
        if self.repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=translate("email_taken", self.locale))
        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        new_user = self.repository.create(new_user)
        publish_welcome_email(new_user.email, new_user.username, self.locale)
        return new_user

    def update_user(self, user_id: UUID, payload: UserUpdate) -> User:
        user = self.get_user(user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return self.repository.update(user)

    def delete_user(self, user_id: UUID) -> None:
        user = self.get_user(user_id)
        self.repository.delete(user)

    def get_settings(self, user_id: UUID) -> UserSettings:
        self.get_user(user_id)
        settings = self.settings_repository.get_by_user_id(user_id)
        if settings is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ayar bulunamadı")
        return settings

    def upsert_settings(self, user_id: UUID, payload: UserSettingsUpsert) -> UserSettings:
        self.get_user(user_id)
        settings = self.settings_repository.get_by_user_id(user_id)
        if settings is None:
            new_settings = UserSettings(user_id=user_id, **payload.model_dump())
            return self.settings_repository.create(new_settings)
        for field, value in payload.model_dump().items():
            setattr(settings, field, value)
        return self.settings_repository.update(settings)

    def get_owner_of_entry(self, entry_id: UUID) -> User:
        owner = self.repository.get_owner_by_library_entry_id(entry_id)
        if owner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu kütüphane kaydına ait kullanıcı bulunamadı")
        return owner

    def get_owners_by_game_title(self, title: str) -> list[User]:
        return self.repository.get_owners_by_game_title(title)


