from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, UserSettingsUpsert, UserSettingsResponse, GameResponse
from services.user_service import UserService
from services.game_service import GameService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return UserService(db).list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService(db).get_user(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(payload)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    return UserService(db).update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    UserService(db).delete_user(user_id)


@router.get("/{user_id}/settings", response_model=UserSettingsResponse)
def get_settings(user_id: int, db: Session = Depends(get_db)):
    return UserService(db).get_settings(user_id)


@router.put("/{user_id}/settings", response_model=UserSettingsResponse)
def upsert_settings(user_id: int, payload: UserSettingsUpsert, db: Session = Depends(get_db)):
    return UserService(db).upsert_settings(user_id, payload)


@router.get("/{user_id}/games", response_model=list[GameResponse])
def list_user_games(user_id: int, title: str | None = Query(default=None), db: Session = Depends(get_db)):
    return GameService(db).list_by_user(user_id, title)
