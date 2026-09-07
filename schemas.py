from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    hashed_password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSettingsUpsert(BaseModel):
    short_max_hours: float = Field(gt=0)
    medium_max_hours: float = Field(gt=0)


class UserSettingsResponse(BaseModel):
    id: int
    user_id: int
    short_max_hours: float
    medium_max_hours: float

    model_config = {"from_attributes": True}


class PlatformAccountCreate(BaseModel):
    user_id: int
    platform_name: str = Field(min_length=1)
    platform_user_id: str = Field(min_length=1)
    access_token: Optional[str] = None


class PlatformAccountResponse(BaseModel):
    id: int
    user_id: int
    platform_name: str
    platform_user_id: str
    connected_at: datetime
    last_synced_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class GameCreate(BaseModel):
    title: str = Field(min_length=1)
    rawg_id: Optional[int] = None
    estimated_hours: float = Field(gt=0)
    cover_image_url: Optional[str] = None


class GameUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    estimated_hours: Optional[float] = Field(default=None, gt=0)
    cover_image_url: Optional[str] = None


class GameResponse(BaseModel):
    id: int
    title: str
    rawg_id: Optional[int]
    estimated_hours: float
    cover_image_url: Optional[str]
    categories: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class LibraryEntryCreate(BaseModel):
    platform_account_id: int
    game_id: int
    completed: bool = False


class LibraryEntryUpdate(BaseModel):
    completed: Optional[bool] = None
    last_played_at: Optional[datetime] = None


class LibraryEntryResponse(BaseModel):
    id: int
    platform_account_id: int
    game_id: int
    completed: bool
    added_at: datetime
    last_played_at: Optional[datetime]

    model_config = {"from_attributes": True}
