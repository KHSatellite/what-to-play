import uuid
from sqlalchemy import Column, String, Float, Integer, Table, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from database import Base


game_category_table = Table(
    "game_categories",
    Base.metadata,
    Column("game_id", Uuid, ForeignKey("games.id"), primary_key=True),
    Column("category_id", Uuid, ForeignKey("categories.id"), primary_key=True),
)


class Game(Base):
    __tablename__ = "games"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    rawg_id = Column(Integer, unique=True, nullable=True)
    rawg_slug = Column(String, nullable=True)
    estimated_hours = Column(Float, nullable=False)
    cover_image_url = Column(String, nullable=True)

    categories = relationship("Category", secondary=game_category_table, back_populates="games")
    library_entries = relationship("LibraryEntry", back_populates="game")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    rawg_id = Column(Integer, unique=True, nullable=True)

    games = relationship("Game", secondary=game_category_table, back_populates="categories")
