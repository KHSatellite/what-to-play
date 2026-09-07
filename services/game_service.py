from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Game
from schemas import GameCreate, GameUpdate
from repositories.game_repository import GameRepository, CategoryRepository
from repositories.user_repository import UserRepository


class GameService:
    def __init__(self, db: Session):
        self.repository = GameRepository(db)
        self.category_repository = CategoryRepository(db)
        self.user_repository = UserRepository(db)

    def list_games(self) -> list[Game]:
        return self.repository.get_all()

    def get_game(self, game_id: int) -> Game:
        game = self.repository.get_by_id(game_id)
        if game is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oyun bulunamadı")
        return game

    def create_game(self, payload: GameCreate) -> Game:
        if payload.rawg_id is not None and self.repository.get_by_rawg_id(payload.rawg_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu rawg_id zaten kayıtlı")
        new_game = Game(**payload.model_dump())
        return self.repository.create(new_game)

    def update_game(self, game_id: int, payload: GameUpdate) -> Game:
        game = self.get_game(game_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(game, field, value)
        return self.repository.update(game)

    def delete_game(self, game_id: int) -> None:
        game = self.get_game(game_id)
        self.repository.delete(game)

    def add_category(self, game_id: int, category_id: int) -> Game:
        game = self.get_game(game_id)
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı")
        if category not in game.categories:
            game.categories.append(category)
            self.repository.update(game)
        return game

    def remove_category(self, game_id: int, category_id: int) -> Game:
        game = self.get_game(game_id)
        category = self.category_repository.get_by_id(category_id)
        if category in game.categories:
            game.categories.remove(category)
            self.repository.update(game)
        return game

    def list_by_user(self, user_id: int, title: str | None = None) -> list[Game]:
        if self.user_repository.get_by_id(user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        return self.repository.get_by_user_id(user_id, title)
