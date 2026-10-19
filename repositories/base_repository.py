from typing import TypeVar, Generic, Type, Optional, Protocol
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session


class HasId(Protocol):
    id: UUID


ModelType = TypeVar("ModelType", bound=HasId)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_all(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def count(self) -> int:
        return self.db.query(func.count(self.model.id)).scalar() or 0

    def get_by_id(self, entity_id: UUID) -> Optional[ModelType]:
        return self.db.get(self.model, entity_id)

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
