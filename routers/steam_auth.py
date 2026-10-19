from uuid import UUID
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from services.steam_openid import build_login_redirect_url, verify_and_extract_steam_id
from services.platform_account_service import PlatformAccountService

router = APIRouter(prefix="/platform-accounts/steam", tags=["steam-auth"])


def _background_import(account_id: UUID) -> None:
    db = SessionLocal()
    try:
        PlatformAccountService(db).import_library(account_id)
    except Exception as e:
        print(f"[background_import] Hata: {e}")
    finally:
        db.close()


@router.get("/login")
def steam_login(user_id: UUID, request: Request):
    base_url = str(request.base_url).rstrip("/")
    return_to = f"{base_url}/platform-accounts/steam/callback?user_id={user_id}"
    return RedirectResponse(build_login_redirect_url(return_to, base_url))


@router.get("/callback")
def steam_callback(request: Request, user_id: UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    steam_id = verify_and_extract_steam_id(dict(request.query_params))
    if steam_id is None:
        return RedirectResponse("/settings?steam_error=1")
    account = PlatformAccountService(db).connect_steam_account(user_id, steam_id)
    background_tasks.add_task(_background_import, account.id)
    return RedirectResponse(f"/settings?steam_connected=1&account_id={account.id}")
