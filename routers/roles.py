from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import RoleCreate, RoleResponse, PermissionCreate, PermissionResponse
from services.role_service import RoleService
from services.token_service import get_current_user
from services.authorization_service import require_permission

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=list[RoleResponse], dependencies=[Depends(get_current_user)])
def list_roles(db: Session = Depends(get_db)):
    return RoleService(db).list_roles()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    return RoleService(db).create_role(payload)


@router.get("/permissions", response_model=list[PermissionResponse], dependencies=[Depends(get_current_user)])
def list_permissions(db: Session = Depends(get_db)):
    return RoleService(db).list_permissions()


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_permission(payload: PermissionCreate, db: Session = Depends(get_db)):
    return RoleService(db).create_permission(payload)


@router.post(
    "/{role_id}/permissions/{permission_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("manage_roles"))],
)
def assign_permission_to_role(role_id: UUID, permission_id: UUID, db: Session = Depends(get_db)):
    return RoleService(db).assign_permission_to_role(role_id, permission_id)

