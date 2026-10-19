import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from database import Base


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    platform_name = Column(String, nullable=False)
    platform_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="platform_accounts")
    library_entries = relationship("LibraryEntry", back_populates="platform_account", cascade="all, delete-orphan")
