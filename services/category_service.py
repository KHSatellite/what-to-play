from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Category
from schemas import CategoryCreate
from repositories.game_repository import CategoryRepository
from services.rawg_client import RawgClient


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)
        self.rawg_client = RawgClient()

    def list_categories(self) -> list[Category]:
        return self.repository.get_all()

    def create_category(self, payload: CategoryCreate) -> Category:
        if self.repository.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu kategori zaten var")
        return self.repository.create(Category(**payload.model_dump()))

    def sync_from_rawg(self) -> list[Category]:
        genres = self.rawg_client.get_genres()
        created = []
        for genre in genres:
            if self.repository.get_by_name(genre["name"]) is None:
                created.append(self.repository.create(Category(name=genre["name"], rawg_id=genre["id"])))
        return created
