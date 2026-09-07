from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


game_category_table = Table(
    "game_categories",
    Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    platform_accounts = relationship("PlatformAccount", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    short_max_hours = Column(Float, default=5.0)
    medium_max_hours = Column(Float, default=15.0)

    user = relationship("User", back_populates="settings")


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_name = Column(String, nullable=False)
    platform_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="platform_accounts")
    library_entries = relationship("LibraryEntry", back_populates="platform_account", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    rawg_id = Column(Integer, unique=True, nullable=True)
    estimated_hours = Column(Float, nullable=False)
    cover_image_url = Column(String, nullable=True)

    categories = relationship("Category", secondary=game_category_table, back_populates="games")
    library_entries = relationship("LibraryEntry", back_populates="game")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", secondary=game_category_table, back_populates="categories")


class LibraryEntry(Base):
    __tablename__ = "library_entries"

    id = Column(Integer, primary_key=True, index=True)
    platform_account_id = Column(Integer, ForeignKey("platform_accounts.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    completed = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_played_at = Column(DateTime, nullable=True)

    platform_account = relationship("PlatformAccount", back_populates="library_entries")
    game = relationship("Game", back_populates="library_entries")
