from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import LibraryEntryCreate, LibraryEntryUpdate, LibraryEntryResponse, UserResponse
from services.library_entry_service import LibraryEntryService
from services.user_service import UserService

router = APIRouter(prefix="/library-entries", tags=["library-entries"])


@router.get("/", response_model=list[LibraryEntryResponse])
def list_entries(platform_account_id: int = Query(...), db: Session = Depends(get_db)):
    return LibraryEntryService(db).list_by_platform_account(platform_account_id)


@router.get("/{entry_id}", response_model=LibraryEntryResponse)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    return LibraryEntryService(db).get_entry(entry_id)


@router.post("/", response_model=LibraryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(payload: LibraryEntryCreate, db: Session = Depends(get_db)):
    return LibraryEntryService(db).create_entry(payload)


@router.put("/{entry_id}", response_model=LibraryEntryResponse)
def update_entry(entry_id: int, payload: LibraryEntryUpdate, db: Session = Depends(get_db)):
    return LibraryEntryService(db).update_entry(entry_id, payload)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    LibraryEntryService(db).delete_entry(entry_id)


@router.get("/{entry_id}/owner", response_model=UserResponse)
def get_entry_owner(entry_id: int, db: Session = Depends(get_db)):
    return UserService(db).get_owner_of_entry(entry_id)
