import requests
import uuid
from seed_admin import seed_admin

BASE = "http://127.0.0.1:8000"
suffix = uuid.uuid4().hex[:6]


def check(label, condition):
    print(f"[{'OK' if condition else 'FAIL'}] {label}")


def register_and_login(username):
    requests.post(f"{BASE}/users/", json={
        "username": username, "email": f"{username}@test.com", "password": "sifre1234"
    })
    r = requests.post(f"{BASE}/auth/token", data={"username": username, "password": "sifre1234"})
    return r.json()["access_token"]


print("=== Kurulum: admin + iki normal kullanici ===")
admin_username = f"admin_{suffix}"
admin_token = register_and_login(admin_username)
admin_headers = {"Authorization": f"Bearer {admin_token}"}

seed_admin(admin_username)

user_b_username = f"userb_{suffix}"
token_b = register_and_login(user_b_username)
headers_b = {"Authorization": f"Bearer {token_b}"}

user_c_username = f"userc_{suffix}"
token_c = register_and_login(user_c_username)
headers_c = {"Authorization": f"Bearer {token_c}"}

r = requests.get(f"{BASE}/users/", headers=admin_headers)
users = r.json()
user_b_id = next(u["id"] for u in users if u["username"] == user_b_username)
user_c_id = next(u["id"] for u in users if u["username"] == user_c_username)

print()
print("=== 1. Rol/yetki OLUSTURMA - herkes yapabilmeli (sadece login yeterli) ===")
r = requests.post(f"{BASE}/roles/", json={"name": f"editor_{suffix}"}, headers=headers_b)
check("Normal kullanici rol olusturabiliyor", r.status_code == 201)
editor_role_id = r.json()["id"]

r = requests.post(f"{BASE}/roles/permissions", json={"name": f"edit_content_{suffix}"}, headers=headers_b)
check("Normal kullanici yetki olusturabiliyor", r.status_code == 201)
edit_permission_id = r.json()["id"]

print()
print("=== 2. Rol/yetki ATAMA - manage_roles gerektirir, normal kullanici YAPAMAMALI ===")
r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}", headers=headers_b)
check("Yetkisiz kullanici baskasina rol atayamiyor (403)", r.status_code == 403)

r = requests.post(f"{BASE}/roles/{editor_role_id}/permissions/{edit_permission_id}", headers=headers_b)
check("Yetkisiz kullanici yetkiyi role baglayamiyor (403)", r.status_code == 403)

print()
print("=== 3. Admin ATAMA yapabilmeli ===")
r = requests.post(f"{BASE}/roles/{editor_role_id}/permissions/{edit_permission_id}", headers=admin_headers)
check("Admin yetkiyi role baglayabiliyor (200)", r.status_code == 200)
check("Yetki rolun listesinde gorunuyor", any(p["id"] == edit_permission_id for p in r.json()["permissions"]))

r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}", headers=admin_headers)
check("Admin rolu kullaniciya atayabiliyor (200)", r.status_code == 200)
check("Rol kullanicinin listesinde gorunuyor", any(role["id"] == editor_role_id for role in r.json()))

print()
print("=== 4. Bulasma testi - userC'nin izni olmamali ===")
r = requests.get(f"{BASE}/users/{user_c_id}/roles", headers=admin_headers)
check("userC'nin hic rolu yok", len(r.json()) == 0)

print()
print("=== 5. Idempotentlik - ayni rolu iki kez atamak hata vermemeli ===")
r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}", headers=admin_headers)
check("Ayni rol tekrar ataninca hala 200 donuyor", r.status_code == 200)

print()
print("=== 6. Olmayan kaynaklar - 404 kontrolleri ===")
fake_id = str(uuid.uuid4())
r = requests.post(f"{BASE}/users/{user_b_id}/roles/{fake_id}", headers=admin_headers)
check("Olmayan role atama -> 404", r.status_code == 404)

r = requests.post(f"{BASE}/users/{fake_id}/roles/{editor_role_id}", headers=admin_headers)
check("Olmayan kullaniciya atama -> 404", r.status_code == 404)

r = requests.post(f"{BASE}/roles/{editor_role_id}/permissions/{fake_id}", headers=admin_headers)
check("Olmayan yetkiyi role baglama -> 404", r.status_code == 404)

print()
print("=== 7. Coklu rol / birlesen yetkiler ===")
r = requests.post(f"{BASE}/roles/", json={"name": f"viewer_{suffix}"}, headers=headers_b)
viewer_role_id = r.json()["id"]
r = requests.post(f"{BASE}/roles/permissions", json={"name": f"view_reports_{suffix}"}, headers=headers_b)
view_permission_id = r.json()["id"]
requests.post(f"{BASE}/roles/{viewer_role_id}/permissions/{view_permission_id}", headers=admin_headers)
requests.post(f"{BASE}/users/{user_b_id}/roles/{viewer_role_id}", headers=admin_headers)

r = requests.get(f"{BASE}/users/{user_b_id}/roles", headers=admin_headers)
role_names = [role["name"] for role in r.json()]
check("userB artik iki role sahip", len(role_names) == 2)

print()
print("=== 8. Ayricalik yukseltme - yeni yetki verilen role sahip kullanici hemen etkileniyor mu ===")
r = requests.post(f"{BASE}/roles/", json={"name": f"future_admin_{suffix}"}, headers=headers_c)
future_role_id = r.json()["id"]
requests.post(f"{BASE}/users/{user_c_id}/roles/{future_role_id}", headers=admin_headers)

r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}", headers=headers_c)
check("userC henuz manage_roles'a sahip degil, atama yapamiyor (403)", r.status_code == 403)

r = requests.post(f"{BASE}/roles/permissions", json={"name": "manage_roles"}, headers=admin_headers)
if r.status_code == 201:
    manage_roles_perm_id = r.json()["id"]
else:
    perms = requests.get(f"{BASE}/roles/permissions", headers=admin_headers).json()
    manage_roles_perm_id = next(p["id"] for p in perms if p["name"] == "manage_roles")

requests.post(f"{BASE}/roles/{future_role_id}/permissions/{manage_roles_perm_id}", headers=admin_headers)

r = requests.post(f"{BASE}/users/{user_b_id}/roles/{viewer_role_id}", headers=headers_c)
check("userC yetki kazanir kazanmaz atama yapabiliyor (cache invalidation dogru calisiyor)", r.status_code == 200)

print()
print("=== 9. Token yok / gecersiz token ayrimi ===")
r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}")
check("Token hic yokken 401 (403 degil)", r.status_code == 401)

r = requests.post(f"{BASE}/users/{user_b_id}/roles/{editor_role_id}", headers={"Authorization": "Bearer gecersiz.token.here"})
check("Gecersiz token ile 401", r.status_code == 401)