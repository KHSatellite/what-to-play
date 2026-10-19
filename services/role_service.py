from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Role, Permission
from schemas import RoleCreate, PermissionCreate
from repositories.role_repository import RoleRepository, PermissionRepository
from repositories.user_repository import UserRepository
from services.permission_cache import invalidate_user_permissions


class RoleService:
    def __init__(self, db: Session):
        self.repository = RoleRepository(db)
        self.permission_repository = PermissionRepository(db)
        self.user_repository = UserRepository(db)

    def list_roles(self) -> list[Role]:
        return self.repository.get_all()

    def create_role(self, payload: RoleCreate) -> Role:
        if self.repository.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu rol zaten var")
        return self.repository.create(Role(name=payload.name))

    def list_permissions(self) -> list[Permission]:
        return self.permission_repository.get_all()

    def create_permission(self, payload: PermissionCreate) -> Permission:
        if self.permission_repository.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu yetki zaten var")
        return self.permission_repository.create(Permission(name=payload.name))

    def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> Role:
        role = self.repository.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol bulunamadı")
        permission = self.permission_repository.get_by_id(permission_id)
        if permission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yetki bulunamadı")
        if permission not in role.permissions:
            role.permissions.append(permission)
            role = self.repository.update(role)
            for user in role.users:
                invalidate_user_permissions(user.id)
        return role

    def assign_role_to_user(self, user_id: UUID, role_id: UUID):
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        role = self.repository.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol bulunamadı")
        if role not in user.roles:
            user.roles.append(role)
            user = self.user_repository.update(user)
            invalidate_user_permissions(user_id)
        return user

    def list_roles_for_user(self, user_id: UUID) -> list[Role]:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
        return user.roles

