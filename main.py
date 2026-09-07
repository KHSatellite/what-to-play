from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import models
from database import engine
from routers import users, platform_accounts, games, categories, library_entries

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ne Oynasam API")

app.include_router(users.router)
app.include_router(platform_accounts.router)
app.include_router(games.router)
app.include_router(categories.router)
app.include_router(library_entries.router)


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Bu kayıt zaten mevcut ya da ilişkili bir veritabanı kısıtını ihlal ediyor"},
    )
