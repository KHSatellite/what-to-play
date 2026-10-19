from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.game_service import SuggestionService

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/showcase")
def showcase(db: Session = Depends(get_db)):
    return SuggestionService(db).get_showcase()
