from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from repositories.role_repository import RoleRepository
from services.token_service import get_current_user
from services.permission_cache import cache_permission, has_cached_permission


def require_permission(permission_name: str):
    def dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if has_cached_permission(current_user.id, permission_name):
            return current_user

        permissions = RoleRepository(db).get_permission_names_for_user(current_user.id)
        if permission_name not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlem için yetkiniz yok")

        for name in permissions:
            cache_permission(current_user.id, name)
        return current_user
    return dependency
