import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Uuid, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class PlayLater(Base):
    __tablename__ = "play_later"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_play_later_user_game"),)

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    game_id = Column(Uuid, ForeignKey("games.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game")
