import sys
import json
import time
import uuid
import pika
import requests
from config import settings
from services.email_service import send_welcome_email
from services.email_queue import QUEUE_NAME

BASE = "http://127.0.0.1:8000"


def check(label, condition):
    print(f"[{'OK' if condition else 'FAIL'}] {label}")


print("=== TEST 1: Gmail SMTP baglantisi (dogrudan, kuyruk devre disi) ===")
if len(sys.argv) < 2:
    print("Kullanim: uv run python test_email_flow.py <kendi_email_adresin>")
    sys.exit(1)

test_email = sys.argv[1]

if not settings.gmail_address or not settings.gmail_app_password:
    check(".env'de GMAIL_ADDRESS / GMAIL_APP_PASSWORD eksik", False)
else:
    try:
        send_welcome_email(test_email, "SmtpTestKullanicisi")
        check("SMTP baglantisi ve gonderim basarili", True)
        print(f"    -> {test_email} kutusuna (ve spam klasorune) bak")
    except Exception as e:
        check(f"SMTP HATASI: {e}", False)

print()
print("=== TEST 2: Kayit olunca kuyruga DOGRU mesaj dusuyor mu ===")
print("(worker.py'nin bu sirada CALISMADIGINDAN emin ol, yoksa mesaji o tuketir)")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_purge(queue=QUEUE_NAME)

suffix = uuid.uuid4().hex[:6]
username = f"queuetest_{suffix}"
email = f"{username}@example.com"

r = requests.post(f"{BASE}/users/", json={"username": username, "email": email, "password": "sifre1234"})
check("Kayit basarili (201)", r.status_code == 201)

time.sleep(0.5)
method, properties, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=True)
if body is None:
    check("Kuyrukta mesaj bulundu", False)
else:
    data = json.loads(body)
    check("Kuyruktaki email dogru", data["email"] == email)
    check("Kuyruktaki username dogru", data["username"] == username)

connection.close()

print()
print("=== TEST 3: RabbitMQ kapaliyken bile kayit BASARILI olmali (dayaniklilik) ===")
print("Bunu otomatik test edemiyoruz, elle dogrula:")
print("  1. Baska bir terminalde: docker compose stop rabbitmq")
print("  2. Sonra: POST /users/ ile yeni bir kayit dene (Swagger'dan olur) - yine 201 donmeli")
print("     ve terminaldeki fastapi loglarinda '[email_queue] Mesaj kuyruga eklenemedi' gormelisin")
print("  3. Bitince: docker compose start rabbitmq")