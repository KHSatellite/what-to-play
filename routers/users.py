from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserSettingsUpsert, UserSettingsResponse,
    GameResponse, RoleResponse, SuggestionResponse, LibraryOverviewItem,
)
from services.user_service import UserService
from services.game_service import GameService, SuggestionService
from services.role_service import RoleService
from services.token_service import get_current_user
from services.authorization_service import require_permission
from services.localization_service import get_locale

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
def list_users(db: Session = Depends(get_db)):
    return UserService(db).list_users()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def get_user(user_id: UUID, db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    return UserService(db, locale).get_user(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    return UserService(db, locale).create_user(payload)


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)):
    return UserService(db).update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    UserService(db).delete_user(user_id)


@router.get("/{user_id}/settings", response_model=UserSettingsResponse, dependencies=[Depends(get_current_user)])
def get_settings(user_id: UUID, db: Session = Depends(get_db)):
    return UserService(db).get_settings(user_id)


@router.put("/{user_id}/settings", response_model=UserSettingsResponse, dependencies=[Depends(get_current_user)])
def upsert_settings(user_id: UUID, payload: UserSettingsUpsert, db: Session = Depends(get_db)):
    return UserService(db).upsert_settings(user_id, payload)


@router.get("/{user_id}/games", response_model=list[GameResponse], dependencies=[Depends(get_current_user)])
def list_user_games(user_id: UUID, title: str | None = Query(default=None), db: Session = Depends(get_db)):
    return GameService(db).list_by_user(user_id, title)


@router.get("/{user_id}/library-overview", response_model=list[LibraryOverviewItem], dependencies=[Depends(get_current_user)])
def get_library_overview(user_id: UUID, db: Session = Depends(get_db)):
    return SuggestionService(db).get_library_overview(user_id)


@router.get("/{user_id}/suggestions", response_model=list[GameResponse], dependencies=[Depends(get_current_user)])
def get_suggestions(
    user_id: UUID,
    category_id: UUID | None = Query(default=None),
    duration: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return SuggestionService(db).get_suggestions(user_id, category_id, duration)


@router.get("/{user_id}/suggestions/random", response_model=SuggestionResponse, dependencies=[Depends(get_current_user)])
def get_random_suggestion(
    user_id: UUID,
    category_id: UUID | None = Query(default=None),
    duration: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return SuggestionService(db).get_random_suggestion(user_id, category_id, duration)


@router.get("/{user_id}/suggestions/combined", response_model=list[SuggestionResponse], dependencies=[Depends(get_current_user)])
def get_combined_suggestions(
    user_id: UUID,
    category_id: UUID | None = Query(default=None),
    duration: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return SuggestionService(db).get_combined_suggestions(user_id, category_id, duration)


@router.get("/{user_id}/roles", response_model=list[RoleResponse], dependencies=[Depends(get_current_user)])
def list_user_roles(user_id: UUID, db: Session = Depends(get_db)):
    return RoleService(db).list_roles_for_user(user_id)


@router.post(
    "/{user_id}/roles/{role_id}",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("manage_roles"))],
)
def assign_role_to_user(user_id: UUID, role_id: UUID, db: Session = Depends(get_db)):
    user = RoleService(db).assign_role_to_user(user_id, role_id)
    return user.roles
