import requests
import time

BASE = "http://127.0.0.1:8000"


def check(label, condition):
    print(f"[{'OK' if condition else 'FAIL'}] {label}")


print("=== 1. Dosya reorganizasyonu sonrasi importlar bozulmus mu (sunucu ayakta mi) ===")
try:
    r = requests.get(f"{BASE}/openapi.json")
    check("Sunucu ayakta ve OpenAPI semasi donuyor", r.status_code == 200)
except requests.exceptions.ConnectionError:
    check("Sunucu ayakta ve OpenAPI semasi donuyor", False)
    print("    -> 'uv run fastapi dev main.py' calisiyor mu kontrol et")
    raise SystemExit(1)

print()
print("=== 2. Bolunmus auth dosyalari dogru calisiyor mu (password/token/authorization) ===")
import uuid
suffix = uuid.uuid4().hex[:6]
r = requests.post(f"{BASE}/users/", json={
    "username": f"newfeat_{suffix}", "email": f"newfeat_{suffix}@test.com", "password": "sifre1234"
})
check("Kayit (password_service.hash_password) calisiyor", r.status_code == 201)

r = requests.post(f"{BASE}/auth/token", data={"username": f"newfeat_{suffix}", "password": "sifre1234"})
check("Login (auth_service.authenticate_user) calisiyor", r.status_code == 200)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

r = requests.get(f"{BASE}/users/", headers=headers)
check("Korumali endpoint (token_service.get_current_user) calisiyor", r.status_code == 200)

r = requests.get(f"{BASE}/users/")
check("Token'siz istek reddediliyor (401)", r.status_code == 401)

print()
print("=== 3. RabbitMQ - genel/ozel ayrimi (rabbitmq_client + email_queue) ===")
print("(worker.py'nin CALISMADIGINDAN emin ol, mesaji o tuketmesin)")
import pika
import json
from config import settings
from services.email_queue import QUEUE_NAME

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_purge(queue=QUEUE_NAME)

r = requests.post(f"{BASE}/users/", json={
    "username": f"queuecheck_{suffix}", "email": f"queuecheck_{suffix}@test.com", "password": "sifre1234"
})
time.sleep(0.5)
method, properties, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=True)
check("Kayit sonrasi kuyruga mesaj dustu", body is not None)
if body:
    check("Mesaj icerigi dogru", json.loads(body)["username"] == f"queuecheck_{suffix}")
connection.close()

print()
print("=== 4. Redis - genel/ozel ayrimi (redis_client + permission_cache) ===")
from services.permission_cache import cache_permission, has_cached_permission, invalidate_user_permissions
from uuid import uuid4

fake_user_id = uuid4()
check("Once cache'te yok", has_cached_permission(fake_user_id, "test_perm") is False)
cache_permission(fake_user_id, "test_perm")
check("cache_permission sonrasi var", has_cached_permission(fake_user_id, "test_perm") is True)
invalidate_user_permissions(fake_user_id)
check("invalidate sonrasi tekrar yok", has_cached_permission(fake_user_id, "test_perm") is False)

print()
print("=== 5. Sentry - DSN'siz calisma ve hatali endpoint ===")
r = requests.get(f"{BASE}/debug/broken")
check("Hatali endpoint 500 donuyor (sunucu cokmedi)", r.status_code == 500)
print("    -> SENTRY_DSN dolu ise, sentry.io panelinde 'Issues' sekmesinde")
print("       bu ZeroDivisionError'i birkac saniye icinde gormelisin")

print()
print("=== 6. Sentry - gercekten yakaliyor mu (yerel, DSN gerektirmeyen dogrulama) ===")
import sentry_sdk

captured = []
original_init = sentry_sdk.init


def patched_init(**kwargs):
    kwargs["before_send"] = lambda event, hint: (captured.append(event), event)[1]
    kwargs["transport"] = None
    return original_init(**kwargs)


sentry_sdk.init = patched_init
from services.monitoring import init_sentry
import config
config.settings.sentry_dsn = "https://fake@fake.ingest.sentry.io/123"
config.settings.environment = "test-dogrulama"
init_sentry()

from fastapi.testclient import TestClient
from main import app as fastapi_app

test_client = TestClient(fastapi_app, raise_server_exceptions=False)
test_client.get("/debug/broken")
check("Sentry hatayi yerel olarak yakaladi", len(captured) > 0)
if captured:
    check("Environment etiketi dogru", captured[0].get("environment") == "test-dogrulama")
    check("Hata tipi dogru (ZeroDivisionError)", captured[0]["exception"]["values"][0]["type"] == "ZeroDivisionError")