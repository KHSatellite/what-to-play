import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
APP_URL = "http://localhost:8000"

_COPY = {
    "tr": {
        "subject": "Ne Oynasam'a hoş geldin, {name}! 🎮",
        "preheader": "Kütüphanen hazır; sıradaki oyunu birlikte seçelim.",
        "title": "Hoş geldin, {name}!",
        "intro": "Artık yüzlerce oyun arasında kararsız kalmak yok. Ne Oynasam, kütüphanendeki oyunları vaktine ve moduna göre süzer, dünyadan yeni öneriler ekler ve kararsızsan senin yerine seçer.",
        "steps_title": "Üç adımda başla",
        "steps": [
            ("Platformlarını bağla", "Ayarlar'dan Steam, Epic Games ya da GOG hesabınla giriş yap; kütüphanen arka planda içe aktarılsın."),
            ("Süre ve kategori seç", "Bugün ne kadar vaktin var, hangi türü istiyorsun? İki soru, 20 öneri."),
            ("Sonra Oyna listeni kur", "Beğendiğin oyunları ★ ile işaretle; asistana 'listemden öner' de, gerisini o halletsin."),
        ],
        "cta": "Uygulamayı aç",
        "tip": "İpucu: Sağ alttaki sohbet balonundan asistana 'kısa bir oyun öner' yazabilirsin.",
        "footer": "Bu e-posta, Ne Oynasam'a kaydolduğun için gönderildi. Sen kaydolmadıysan görmezden gelebilirsin.",
        "plain": "Merhaba {name},\n\nNe Oynasam'a hoş geldin! Ayarlar'dan Steam / Epic / GOG hesabını bağla, süre ve kategori seç, 20 öneri al. Beğendiklerini ★ ile Sonra Oyna listene ekle.\n\n{url}\n\nİyi oyunlar!",
    },
    "en": {
        "subject": "Welcome to Ne Oynasam, {name}! 🎮",
        "preheader": "Your library is ready; let's pick your next game together.",
        "title": "Welcome, {name}!",
        "intro": "No more staring at hundreds of games. Ne Oynasam filters your library by the time you have and the mood you're in, adds fresh picks from the wider world, and chooses for you when you can't.",
        "steps_title": "Get started in three steps",
        "steps": [
            ("Connect your platforms", "Sign in with Steam, Epic Games or GOG from Settings; your library imports in the background."),
            ("Pick time and genre", "How much time do you have today, what genre are you after? Two questions, 20 picks."),
            ("Build your Play Later list", "Star games you like; tell the assistant 'pick from my list' and let it decide."),
        ],
        "cta": "Open the app",
        "tip": "Tip: Use the chat bubble at the bottom right and type 'recommend a short game'.",
        "footer": "You're receiving this because you signed up for Ne Oynasam. If that wasn't you, feel free to ignore it.",
        "plain": "Hi {name},\n\nWelcome to Ne Oynasam! Connect Steam / Epic / GOG from Settings, pick time and genre, get 20 picks. Star the ones you like to build your Play Later list.\n\n{url}\n\nHappy gaming!",
    },
}


def _html(c: dict, name: str) -> str:
    steps = "".join(
        f"""<tr><td style="padding:10px 0;vertical-align:top;width:36px">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#7c5cff,#22d3ee);color:#fff;font-weight:700;font-size:13px;line-height:28px;text-align:center">{i}</div>
            </td><td style="padding:10px 0 10px 12px;vertical-align:top">
              <div style="font-weight:600;color:#eef1f7">{t}</div>
              <div style="color:#9aa3b5;font-size:14px;line-height:1.5">{d}</div>
            </td></tr>"""
        for i, (t, d) in enumerate(c["steps"], 1)
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background:#070a12;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#eef1f7">
<span style="display:none;max-height:0;overflow:hidden">{c['preheader']}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#070a12;padding:32px 16px">
<tr><td align="center">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%">
  <tr><td style="padding:0 0 20px;font-weight:800;letter-spacing:.12em;font-size:15px">NE<span style="color:#7c5cff">OYNASAM</span></td></tr>
  <tr><td style="background:linear-gradient(135deg,#1b1740,#0d1220);border:1px solid #2a2f45;border-radius:16px;padding:32px 28px">
    <h1 style="margin:0 0 12px;font-size:26px;line-height:1.2">{c['title'].format(name=name)}</h1>
    <p style="margin:0 0 22px;color:#c3c9d6;font-size:15px;line-height:1.6">{c['intro']}</p>
    <div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#22d3ee;font-weight:700;margin-bottom:6px">{c['steps_title']}</div>
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%">{steps}</table>
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:22px 0 8px"><tr><td style="border-radius:999px;background:linear-gradient(135deg,#7c5cff,#22d3ee)">
      <a href="{APP_URL}" style="display:inline-block;padding:13px 26px;color:#fff;text-decoration:none;font-weight:700;font-size:15px">{c['cta']} →</a>
    </td></tr></table>
    <p style="margin:16px 0 0;color:#9aa3b5;font-size:13px;line-height:1.5">{c['tip']}</p>
  </td></tr>
  <tr><td style="padding:20px 8px 0;color:#6b7280;font-size:12px;line-height:1.5;text-align:center">{c['footer']}<br>Kadir Hanbaba · <a href="https://github.com/KHSatellite" style="color:#7c5cff;text-decoration:none">github.com/KHSatellite</a></td></tr>
</table></td></tr></table></body></html>"""


def send_welcome_email(to_email: str, username: str, lang: str = "tr") -> None:
    if not settings.gmail_address or not settings.gmail_app_password:
        print(f"[email] Gmail ayarlari eksik, '{to_email}' adresine mail gonderilemedi (atlaniyor).")
        return

    c = _COPY.get(lang, _COPY["tr"])
    message = MIMEMultipart("alternative")
    message["Subject"] = c["subject"].format(name=username)
    message["From"] = f"Ne Oynasam <{settings.gmail_address}>"
    message["To"] = to_email
    message.attach(MIMEText(c["plain"].format(name=username, url=APP_URL), "plain", "utf-8"))
    message.attach(MIMEText(_html(c, username), "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.sendmail(settings.gmail_address, to_email, message.as_string())
