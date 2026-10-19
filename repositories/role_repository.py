from uuid import UUID
from sqlalchemy.orm import Session
from models import Role, Permission, user_role_table, role_permission_table
from repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_permission_names_for_user(self, user_id: UUID) -> set[str]:
        rows = (
            self.db.query(Permission.name)
            .join(role_permission_table, role_permission_table.c.permission_id == Permission.id)
            .join(Role, Role.id == role_permission_table.c.role_id)
            .join(user_role_table, user_role_table.c.role_id == Role.id)
            .filter(user_role_table.c.user_id == user_id)
            .all()
        )
        return {row[0] for row in rows}


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: Session):
        super().__init__(db, Permission)

    def get_by_name(self, name: str) -> Permission | None:
        return self.db.query(Permission).filter(Permission.name == name).first()
