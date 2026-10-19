import json
from services.rabbitmq_client import publish

QUEUE_NAME = "welcome_emails"


def publish_welcome_email(email: str, username: str, lang: str = "tr") -> None:
    try:
        message = json.dumps({"email": email, "username": username, "lang": lang})
        publish(QUEUE_NAME, message)
    except Exception as e:
        print(f"[email_queue] Mesaj kuyruga eklenemedi: {e}")
