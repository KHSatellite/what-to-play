import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from database import Base


class LibraryEntry(Base):
    __tablename__ = "library_entries"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    platform_account_id = Column(Uuid, ForeignKey("platform_accounts.id"), nullable=False)
    game_id = Column(Uuid, ForeignKey("games.id"), nullable=False)
    platform_game_id = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_played_at = Column(DateTime, nullable=True)

    platform_account = relationship("PlatformAccount", back_populates="library_entries")
    game = relationship("Game", back_populates="library_entries")
