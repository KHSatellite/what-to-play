from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import PlayLater
from repositories.play_later_repository import PlayLaterRepository
from repositories.game_repository import GameRepository
from services.game_service import GameService, SuggestionService


class PlayLaterService:
    def __init__(self, db: Session):
        self.repository = PlayLaterRepository(db)
        self.game_repository = GameRepository(db)
        self.game_service = GameService(db)

    def list_items(self, user_id: UUID) -> list[dict]:
        by_game = self.repository.platforms_by_game(user_id)
        out = []
        for row in self.repository.list_for_user(user_id):
            g = row.game
            plats = by_game.get(g.id, [])
            platforms = sorted({p for p, _ in plats}, key=lambda p: (p != "steam", p))
            pgid = next((pg for p, pg in plats if p == "steam"), plats[0][1] if plats else None)
            out.append({
                "id": g.id,
                "title": g.title,
                "estimated_hours": g.estimated_hours,
                "cover_image_url": g.cover_image_url,
                "source": "library" if platforms else "rawg",
                "platform": platforms[0] if platforms else None,
                "platforms": platforms,
                "link": SuggestionService._library_link(g, platforms[0] if platforms else "", pgid),
                "rawg_id": g.rawg_id,
                "added_at": row.added_at,
            })
        return out

    def ids(self, user_id: UUID) -> list[dict]:
        return [{"game_id": r.game_id, "rawg_id": r.game.rawg_id} for r in self.repository.list_for_user(user_id)]

    def add(self, user_id: UUID, game_id: UUID | None, rawg_id: int | None) -> dict:
        if game_id is None and rawg_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="game_id ya da rawg_id gerekli")
        game = self.game_repository.get_by_id(game_id) if game_id else self.game_repository.get_by_rawg_id(rawg_id)
        if game is None and rawg_id is not None:
            try:
                game, _ = self.game_service.upsert_from_rawg(self.game_service.rawg.get_game(rawg_id))
            except Exception:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RAWG'da oyun bulunamadı")
        if game is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oyun bulunamadı")
        if self.repository.get(user_id, game.id) is None:
            self.repository.create(PlayLater(user_id=user_id, game_id=game.id))
        return {"game_id": game.id}

    def remove(self, user_id: UUID, game_id: UUID) -> None:
        row = self.repository.get(user_id, game_id)
        if row:
            self.repository.delete(row)
