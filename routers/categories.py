from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import CategoryCreate, CategoryResponse
from services.category_service import CategoryService
from services.token_service import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return CategoryService(db).list_categories()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService(db).create_category(payload)


@router.post("/sync-from-rawg", response_model=list[CategoryResponse])
def sync_categories_from_rawg(db: Session = Depends(get_db)):
    return CategoryService(db).sync_from_rawg()

