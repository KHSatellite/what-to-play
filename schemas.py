from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSettingsUpsert(BaseModel):
    short_max_hours: float = Field(gt=0)
    medium_max_hours: float = Field(gt=0)


class UserSettingsResponse(BaseModel):
    id: UUID
    user_id: UUID
    short_max_hours: float
    medium_max_hours: float

    model_config = {"from_attributes": True}


class PlatformAccountCreate(BaseModel):
    user_id: UUID
    platform_name: str = Field(min_length=1)
    platform_user_id: str = Field(min_length=1)
    access_token: Optional[str] = None


class PlatformAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    platform_name: str
    platform_user_id: str
    connected_at: datetime
    last_synced_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)


class CategoryResponse(BaseModel):
    id: UUID
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
    id: UUID
    title: str
    rawg_id: Optional[int]
    estimated_hours: float
    cover_image_url: Optional[str]
    categories: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class LibraryEntryCreate(BaseModel):
    platform_account_id: UUID
    game_id: UUID
    completed: bool = False


class LibraryEntryUpdate(BaseModel):
    completed: Optional[bool] = None
    last_played_at: Optional[datetime] = None


class LibraryEntryResponse(BaseModel):
    id: UUID
    platform_account_id: UUID
    game_id: UUID
    completed: bool
    added_at: datetime
    last_played_at: Optional[datetime]

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PermissionCreate(BaseModel):
    name: str = Field(min_length=1)


class PermissionResponse(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str = Field(min_length=1)


class RoleResponse(BaseModel):
    id: UUID
    name: str
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}


class SuggestionResponse(BaseModel):
    id: Optional[UUID] = None
    title: str
    estimated_hours: float
    cover_image_url: Optional[str] = None
    source: str
    platform: Optional[str] = None
    platforms: list[str] = []
    link: Optional[str] = None
    rawg_id: Optional[int] = None


class PlayLaterAdd(BaseModel):
    game_id: Optional[UUID] = None
    rawg_id: Optional[int] = None


class LibraryOverviewEntry(BaseModel):
    entry_id: UUID
    platform_name: str
    completed: bool


class LibraryOverviewItem(BaseModel):
    game_id: UUID
    title: str
    estimated_hours: float
    cover_image_url: Optional[str] = None
    completed: bool
    categories: list[str] = []
    platforms: list[str] = []
    entries: list[LibraryOverviewEntry] = []
    link: Optional[str] = None


class ConnectCodeRequest(BaseModel):
    platform: str = Field(min_length=1)
    code: str = Field(min_length=1)


class ManualAddRequest(BaseModel):
    platform: str = Field(min_length=1)
    rawg_id: int


class SteamImportResult(BaseModel):
    imported: int
    skipped: int
    total: int
