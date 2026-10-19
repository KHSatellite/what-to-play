from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import PlatformAccountCreate, PlatformAccountResponse, SteamImportResult, ConnectCodeRequest, ManualAddRequest, LibraryEntryResponse
from services.platform_account_service import PlatformAccountService
from services.token_service import get_current_user

router = APIRouter(prefix="/platform-accounts", tags=["platform-accounts"])


@router.get("/connectors")
def list_connectors(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlatformAccountService(db).list_connectors(user.id)


@router.post("/connect-code", response_model=PlatformAccountResponse)
def connect_with_code(payload: ConnectCodeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlatformAccountService(db).connect_with_code(user.id, payload.platform, payload.code)


@router.get("/rawg-search")
def rawg_search(q: str = Query(min_length=2), _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlatformAccountService(db).search_rawg(q)


@router.post("/manual-add", response_model=LibraryEntryResponse, status_code=status.HTTP_201_CREATED)
def manual_add(payload: ManualAddRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlatformAccountService(db).add_manual_game(user.id, payload.platform, payload.rawg_id)


@router.get("/", response_model=list[PlatformAccountResponse], dependencies=[Depends(get_current_user)])
def list_accounts(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    return PlatformAccountService(db).list_by_user(user_id)


@router.get("/{account_id}", response_model=PlatformAccountResponse, dependencies=[Depends(get_current_user)])
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    return PlatformAccountService(db).get_account(account_id)


@router.post("/", response_model=PlatformAccountResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_account(payload: PlatformAccountCreate, db: Session = Depends(get_db)):
    return PlatformAccountService(db).create_account(payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_account(account_id: UUID, db: Session = Depends(get_db)):
    PlatformAccountService(db).delete_account(account_id)


@router.post("/{account_id}/import", response_model=SteamImportResult, dependencies=[Depends(get_current_user)])
def import_library(account_id: UUID, db: Session = Depends(get_db)):
    return PlatformAccountService(db).import_library(account_id)


@router.get("/{account_id}/import-status", dependencies=[Depends(get_current_user)])
def import_status(account_id: UUID, db: Session = Depends(get_db)):
    return PlatformAccountService(db).get_import_status(account_id)
