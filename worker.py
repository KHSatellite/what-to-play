import json
from services.rabbitmq_client import consume
from services.email_service import send_welcome_email
from services.email_queue import QUEUE_NAME


def handle_message(body: bytes) -> None:
    data = json.loads(body)
    print(f"[worker] '{data['email']}' adresine hosgeldin maili gonderiliyor...")
    try:
        send_welcome_email(data["email"], data["username"], data.get("lang", "tr"))
        print(f"[worker] gonderildi: {data['email']}")
    except Exception as e:
        print(f"[worker] HATA: {e}")


if __name__ == "__main__":
    print("[worker] Kuyruk dinleniyor, cikmak icin CTRL+C...")
    consume(QUEUE_NAME, handle_message)
