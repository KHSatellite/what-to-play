from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import PlatformAccountCreate, PlatformAccountResponse
from services.platform_account_service import PlatformAccountService

router = APIRouter(prefix="/platform-accounts", tags=["platform-accounts"])


@router.get("/", response_model=list[PlatformAccountResponse])
def list_accounts(user_id: int = Query(...), db: Session = Depends(get_db)):
    return PlatformAccountService(db).list_by_user(user_id)


@router.get("/{account_id}", response_model=PlatformAccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return PlatformAccountService(db).get_account(account_id)


@router.post("/", response_model=PlatformAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: PlatformAccountCreate, db: Session = Depends(get_db)):
    return PlatformAccountService(db).create_account(payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    PlatformAccountService(db).delete_account(account_id)
