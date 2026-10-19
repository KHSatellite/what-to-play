from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
import models
from database import Base, engine, SessionLocal
from routers import auth, users, platform_accounts, games, categories, library_entries, roles, debug, chat, steam_auth, public, play_later
from services.localization_service import resolve_locale, translate
from services.monitoring import init_sentry
from services.category_service import CategoryService

init_sentry()

Base.metadata.create_all(bind=engine)


def sync_categories_on_startup() -> None:
    db = SessionLocal()
    try:
        service = CategoryService(db)
        if not service.list_categories():
            try:
                service.sync_from_rawg()
                print("[startup] Kategoriler RAWG'dan senkronize edildi.")
            except Exception as e:
                print(f"[startup] Kategori senkronizasyonu basarisiz: {e}")
    finally:
        db.close()


sync_categories_on_startup()


class SPAStaticFiles(StaticFiles):
    """Bilinmeyen yollar için index.html döner; React Router'ın URL'leri böyle çalışır."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


app = FastAPI(title="Ne Oynasam API")

for r in (auth, users, platform_accounts, games, categories, library_entries, roles, debug, chat, steam_auth, public, play_later):
    app.include_router(r.router)


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    locale = resolve_locale(request.headers.get("accept-language"))
    return JSONResponse(status_code=409, content={"detail": translate("integrity_conflict", locale)})


app.mount("/", SPAStaticFiles(directory="static", html=True), name="static")
