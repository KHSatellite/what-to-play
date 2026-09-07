from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import GameCreate, GameUpdate, GameResponse, UserResponse
from services.game_service import GameService
from services.user_service import UserService

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=list[GameResponse])
def list_games(db: Session = Depends(get_db)):
    return GameService(db).list_games()


@router.get("/owners", response_model=list[UserResponse])
def list_owners_by_title(title: str = Query(...), db: Session = Depends(get_db)):
    return UserService(db).get_owners_by_game_title(title)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    return GameService(db).get_game(game_id)


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreate, db: Session = Depends(get_db)):
    return GameService(db).create_game(payload)


@router.put("/{game_id}", response_model=GameResponse)
def update_game(game_id: int, payload: GameUpdate, db: Session = Depends(get_db)):
    return GameService(db).update_game(game_id, payload)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    GameService(db).delete_game(game_id)


@router.post("/{game_id}/categories/{category_id}", response_model=GameResponse)
def add_category(game_id: int, category_id: int, db: Session = Depends(get_db)):
    return GameService(db).add_category(game_id, category_id)


@router.delete("/{game_id}/categories/{category_id}", response_model=GameResponse)
def remove_category(game_id: int, category_id: int, db: Session = Depends(get_db)):
    return GameService(db).remove_category(game_id, category_id)
