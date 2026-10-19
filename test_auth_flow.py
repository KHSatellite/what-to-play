import requests
import uuid
from seed_admin import seed_admin

BASE = "http://127.0.0.1:8000"
suffix = uuid.uuid4().hex[:6]


def check(label, condition):
    print(f"[{'OK' if condition else 'FAIL'}] {label}")


print("=== 1. Kayit ve giris ===")
r = requests.post(f"{BASE}/users/", json={
    "username": f"testuser_{suffix}",
    "email": f"testuser_{suffix}@test.com",
    "password": "guclu-sifre-123"
})
check("Kayit basarili (201)", r.status_code == 201)
user_id = r.json()["id"]

r = requests.post(f"{BASE}/auth/token", data={
    "username": f"testuser_{suffix}",
    "password": "guclu-sifre-123"
})
check("Giris basarili (200)", r.status_code == 200)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print()
print("=== 2. Authentication kontrolu ===")
r = requests.get(f"{BASE}/users/{user_id}")
check("Token olmadan 401 donuyor", r.status_code == 401)

r = requests.get(f"{BASE}/users/{user_id}", headers=headers)
check("Token ile 200 donuyor", r.status_code == 200)

print()
print("=== 3. Bootstrap: bu kullaniciyi manage_roles yetkisiyle admin yap ===")
seed_admin(f"testuser_{suffix}")

print()
print("=== 4. Rol ve yetki olusturma ===")
r = requests.post(f"{BASE}/roles/", json={"name": f"test_admin_{suffix}"}, headers=headers)
check("Rol olusturuldu (201)", r.status_code == 201)
role_id = r.json()["id"]

r = requests.post(f"{BASE}/roles/permissions", json={"name": f"manage_games_{suffix}"}, headers=headers)
check("Yetki olusturuldu (201)", r.status_code == 201)
permission_id = r.json()["id"]

print()
print("=== 5. Yetkiyi role, rolu kullaniciya baglama ===")
r = requests.post(f"{BASE}/roles/{role_id}/permissions/{permission_id}", headers=headers)
check("Yetki role baglandi (200)", r.status_code == 200)
check("Rolun yetkileri arasinda gorunuyor", any(p["id"] == permission_id for p in r.json()["permissions"]))

r = requests.post(f"{BASE}/users/{user_id}/roles/{role_id}", headers=headers)
check("Rol kullaniciya atandi (200)", r.status_code == 200)
check("Kullanicinin rolleri arasinda gorunuyor", any(role["id"] == role_id for role in r.json()))

r = requests.get(f"{BASE}/users/{user_id}/roles", headers=headers)
check("GET roller listesinde dogrulandi", any(role["id"] == role_id for role in r.json()))

print()
print("=== 6. Authorization (yetki) kontrolu ===")
r = requests.post(f"{BASE}/games/", json={"title": f"Test Oyunu {suffix}", "estimated_hours": 5}, headers=headers)
game_id = r.json()["id"]

r = requests.post(f"{BASE}/roles/permissions", json={"name": "manage_games"}, headers=headers)
if r.status_code == 201:
    manage_games_permission_id = r.json()["id"]
else:
    r2 = requests.get(f"{BASE}/roles/permissions", headers=headers)
    manage_games_permission_id = next(p["id"] for p in r2.json() if p["name"] == "manage_games")

r = requests.post(f"{BASE}/roles/{role_id}/permissions/{manage_games_permission_id}", headers=headers)
check("manage_games yetkisi role baglandi", r.status_code == 200)

r = requests.post(f"{BASE}/users/", json={
    "username": f"yetkisiz_{suffix}",
    "email": f"yetkisiz_{suffix}@test.com",
    "password": "guclu-sifre-123"
})
r = requests.post(f"{BASE}/auth/token", data={
    "username": f"yetkisiz_{suffix}",
    "password": "guclu-sifre-123"
})
other_token = r.json()["access_token"]
other_headers = {"Authorization": f"Bearer {other_token}"}

r = requests.delete(f"{BASE}/games/{game_id}", headers=other_headers)
check("Yetkisiz kullanici silemiyor (403)", r.status_code == 403)

r = requests.delete(f"{BASE}/games/{game_id}", headers=headers)
check("Yetkili kullanici silebiliyor (204)", r.status_code == 204)

print()
print("=== 7. Localization kontrolu ===")
r = requests.get(f"{BASE}/users/00000000-0000-0000-0000-000000000000",
                  headers={**headers, "Accept-Language": "tr"})
print("TR mesaj:", r.json()["detail"])
r = requests.get(f"{BASE}/users/00000000-0000-0000-0000-000000000000",
                  headers={**headers, "Accept-Language": "en"})
print("EN mesaj:", r.json()["detail"])
