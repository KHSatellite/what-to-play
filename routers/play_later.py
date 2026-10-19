from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import PlayLaterAdd, SuggestionResponse
from services.play_later_service import PlayLaterService
from services.token_service import get_current_user

router = APIRouter(prefix="/play-later", tags=["play-later"])


@router.get("/", response_model=list[SuggestionResponse])
def list_play_later(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlayLaterService(db).list_items(user.id)


@router.get("/ids")
def play_later_ids(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlayLaterService(db).ids(user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_play_later(payload: PlayLaterAdd, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlayLaterService(db).add(user.id, payload.game_id, payload.rawg_id)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_play_later(game_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PlayLaterService(db).remove(user.id, game_id)
