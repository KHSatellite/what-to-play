from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Category
from schemas import CategoryCreate
from repositories.game_repository import CategoryRepository


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def list_categories(self) -> list[Category]:
        return self.repository.get_all()

    def create_category(self, payload: CategoryCreate) -> Category:
        if self.repository.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu kategori zaten var")
        new_category = Category(**payload.model_dump())
        return self.repository.create(new_category)
