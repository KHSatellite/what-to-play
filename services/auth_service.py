from sqlalchemy.orm import Session
from models import User
from repositories.user_repository import UserRepository
from services.password_service import verify_password


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = UserRepository(db).get_by_username(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
