import requests
import uuid

BASE = "http://127.0.0.1:8000"
suffix = uuid.uuid4().hex[:6]

r = requests.post(f"{BASE}/users/", json={
    "username": f"kadir_{suffix}",
    "email": f"kadir_{suffix}@test.com",
    "hashed_password": "x"
})
user_id = r.json()["id"]
print("user:", r.status_code, r.json())

r = requests.post(f"{BASE}/platform-accounts/", json={
    "user_id": user_id,
    "platform_name": "steam",
    "platform_user_id": suffix
})
account_id = r.json()["id"]
print("account:", r.status_code, r.json())

titles = ["Hollow Knight", "Grand Theft Auto 5", "Portal 2", "Need for Speed 5"]
game_ids = []
for t in titles:
    r = requests.post(f"{BASE}/games/", json={"title": t, "estimated_hours": 10})
    game_ids.append(r.json()["id"])
print("games:", game_ids)

entry_ids = []
for gid in game_ids:
    r = requests.post(f"{BASE}/library-entries/", json={
        "platform_account_id": account_id,
        "game_id": gid
    })
    entry_ids.append(r.json()["id"])
print("entries:", entry_ids)

print()
print("--- TEST: kullanicinin tum oyunlari ---")
r = requests.get(f"{BASE}/users/{user_id}/games")
print(r.status_code, [g["title"] for g in r.json()])

print()
print("--- TEST: baslikta '5' gecenler ---")
r = requests.get(f"{BASE}/users/{user_id}/games", params={"title": "5"})
print(r.status_code, [g["title"] for g in r.json()])

print()
print("--- TEST: entry -> sahibi ---")
r = requests.get(f"{BASE}/library-entries/{entry_ids[0]}/owner")
print(r.status_code, r.json())

print()
print("--- TEST: olmayan kullanici 404 vermeli ---")
r = requests.get(f"{BASE}/users/999999/games")
print(r.status_code, r.json())

print()
print("--- baslikta belirli kelime gecen oyuna sahip kullanicilar ---")
r = requests.get(f"{BASE}/games/owners", params={"title": "5"})
print(r.status_code, [u["username"] for u in r.json()])