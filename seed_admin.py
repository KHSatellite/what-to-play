import sys
from database import SessionLocal
from models import Role, Permission
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository, PermissionRepository


def seed_admin(username: str) -> None:
    db = SessionLocal()
    try:
        user_repository = UserRepository(db)
        role_repository = RoleRepository(db)
        permission_repository = PermissionRepository(db)

        user = user_repository.get_by_username(username)
        if user is None:
            print(f"'{username}' adinda bir kullanici bulunamadi. Once kayit olmali.")
            return

        role = role_repository.get_by_name("superadmin")
        if role is None:
            role = role_repository.create(Role(name="superadmin"))
            print("superadmin rolu olusturuldu")

        permission = permission_repository.get_by_name("manage_roles")
        if permission is None:
            permission = permission_repository.create(Permission(name="manage_roles"))
            print("manage_roles yetkisi olusturuldu")

        if permission not in role.permissions:
            role.permissions.append(permission)
            role_repository.update(role)
            print("manage_roles yetkisi superadmin rolune baglandi")

        if role not in user.roles:
            user.roles.append(role)
            user_repository.update(user)
            print(f"superadmin rolu '{username}' kullanicisina atandi")
        else:
            print(f"'{username}' zaten superadmin rolune sahip")

        print("Bootstrap tamamlandi.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanim: uv run python seed_admin.py <kullanici_adi>")
        sys.exit(1)
    seed_admin(sys.argv[1])
