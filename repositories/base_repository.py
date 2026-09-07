from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_all(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def create(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)
        self.db.commit()
