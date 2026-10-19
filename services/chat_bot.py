import random
import re
from collections import Counter
from sqlalchemy.orm import Session
from models import User
from repositories.play_later_repository import PlayLaterRepository
from repositories.user_repository import UserSettingsRepository
from repositories.platform_account_repository import PlatformAccountRepository
from services.game_service import SuggestionService, DEFAULT_SHORT_MAX_HOURS, DEFAULT_MEDIUM_MAX_HOURS
from services.platforms import CONNECTORS, MANUAL_PLATFORMS

CONTACT_EMAIL = "hanbaba.kadir8@gmail.com"
_TR = str.maketrans("çğıöşüâîû", "cgiosuaiu")

# Yanıt metinleri; {..} yer tutucuları format() ile doldurulur
_T = {
    "tr": {
        "empty": "Bir şey yazarsan yardımcı olayım 🙂",
        "hello": "Selam {name}! Ne oynayacağını bulmana yardım edeyim. 'oyun öner' yaz ya da 'yardım' de.",
        "thanks": ["Ne demek, iyi oyunlar! 🎮", "Rica ederim. Bugün bir şeyler bitir bakalım 😄"],
        "login": "Bunun için önce giriş yapman gerekiyor. Sağ üstten Giriş / Kayıt Ol'a tıklayabilirsin.",
        "no_lib": "Kütüphanende oynanmamış oyun bulamadım. Ayarlar'dan Steam, Epic ya da GOG bağlarsan oradan seçebilirim; ya da Kütüphanem → Oyun ekle ile elle ekleyebilirsin.",
        "suggest": "🎲 {title}{hours} — {plat}. {tail}{link}",
        "hours": " (~{h:.0f} saat)", "lib_word": "kütüphanen",
        "tails": ["Bence bugünlük bu.", "Bir şans ver derim.", "Kararsızsan Oyun Öner sayfasında 20 tane daha var."],
        "stats_empty": "Kütüphanen şu an boş. Ayarlar → Platform bağlantıları'ndan Steam/Epic/GOG bağlayarak başlayabilirsin.",
        "stats": "📚 Kütüphanende {n} oyun var ({plats}). {done} tanesini bitirmişsin, toplam tahmini süre ~{hours:,.0f} saat. Sonra Oyna listende {later} oyun bekliyor.",
        "later_empty": "Sonra Oyna listen boş. Kartların köşesindeki ☆ simgesine dokunarak ekleyebilirsin.",
        "later": "⭐ Sonra Oyna listende: {names}{more}. İstersen 'listemden öner' de, birini seçeyim.",
        "later_more": " ve {n} tane daha",
        "later_pick": "⭐ Listenden seçtim: {title}. Hadi başla!",
        "dur_guest": "Varsayılan eşikler: kısa ≤ {s:.0f} saat, orta ≤ {m:.0f} saat, üstü uzun. Kayıt olunca kendine göre ayarlayabilirsin.",
        "dur": "⏱ Senin için: kısa oyun ≤ {s:g} saat, orta ≤ {m:g} saat, üstü uzun. Ayarlar → Süre tercihlerim'den değiştirebilirsin.",
        "steam": "Steam: Ayarlar → Platform bağlantıları → 'Steam ile bağlan'. Steam'in kendi giriş sayfasına gider, geri döndüğünde kütüphane arka planda içe aktarılır. Not: Steam profilinde 'Oyun detayları' Herkese Açık olmalı.",
        "epic": "Epic: 'Epic ile bağlan' yeni sekmede Epic girişini açar. Giriş sonrası ekranda 'authorizationCode' içeren bir metin görünür; o metni kartın altındaki kutuya yapıştırıp 'Bağla ve içe aktar' de. Kod tek kullanımlık.",
        "gog": "GOG: 'GOG ile bağlan' sonrası giriş yap; açılan sayfanın adres çubuğundaki adresi (embed.gog.com/on_login_success?...code=...) komple kopyalayıp kutuya yapıştır. Kod ~1 dakika geçerli.",
        "manual": "{list} gibi platformlar üçüncü taraf girişine izin vermiyor. Bu oyunları Kütüphanem → '＋ Oyun ekle' ile RAWG'da arayıp platformunu seçerek ekleyebilirsin; rozet ve öneriler aynı şekilde çalışır.",
        "conn_none": "Henüz bağlı platform yok. Ayarlar → Platform bağlantıları'ndan Steam, Epic ya da GOG bağlayabilirsin.",
        "conn_auto": "bağlı hesaplar: {x}", "conn_manual": "elle eklenen: {x}",
        "help": "Şunları sorabilirsin:\n• 'oyun öner' / 'kısa bir oyun öner' — kütüphanenden rastgele seçerim\n• 'kaç oyunum var' — kütüphane özeti\n• 'sonra oyna listem' / 'listemden öner'\n• 'steam nasıl bağlanır' (epic, gog, ubisoft…)\n• 'süre ayarları', 'kategoriler', 'tema'\n• 'iletişim' — geliştiriciye ulaşmak için",
        "cats": "Kategoriler RAWG'ın türlerinden gelir (Action, RPG, Indie…); bir oyun birden fazla kategoride olabilir. Oyun Öner sayfasında kategori seçince hem kütüphanenden hem RAWG'dan o türde öneri gelir.",
        "theme": "Tema: sağ üstteki avatar menüsündeki renk noktaları ya da Ayarlar → Tema. Karışım, PlayStation, Netflix ve Neon var. Dil de aynı menüden değişiyor.",
        "account": "Şifre sıfırlama ve hesap silme henüz arayüzde yok; {mail} adresine yazarsan hallederim.",
        "contact": "Bir sorun varsa {mail} adresine yazabilirsin; mümkünse hangi sayfada ve ne yaparken olduğunu ekle. Küçük ipucu: sayfayı Ctrl+Shift+R ile yenilemek çoğu görüntü sorununu çözer.",
        "fallback": ["Bunu tam anlayamadım. 'oyun öner' dersen kütüphanenden seçerim.", "Bunu tam anlayamadım. 'yardım' yazarsan neler yapabildiğimi gösteririm.", "Bunu tam anlayamadım. 'kaç oyunum var' ya da 'steam nasıl bağlanır' gibi sorabilirsin."],
        "guest": "misafir",
    },
    "en": {
        "empty": "Type something and I'll help 🙂",
        "hello": "Hi {name}! I can help you pick something to play. Try 'recommend a game' or 'help'.",
        "thanks": ["Anytime, happy gaming! 🎮", "You're welcome. Go finish something today 😄"],
        "login": "You need to log in for that. Use Log in / Sign up at the top right.",
        "no_lib": "I couldn't find an unplayed game in your library. Connect Steam, Epic or GOG from Settings, or add games manually via My Library → Add game.",
        "suggest": "🎲 {title}{hours} — {plat}. {tail}{link}",
        "hours": " (~{h:.0f} h)", "lib_word": "your library",
        "tails": ["That's my pick for today.", "Give it a shot.", "Undecided? There are 20 more on the Recommend page."],
        "stats_empty": "Your library is empty. Connect Steam/Epic/GOG from Settings → Platform connections to get started.",
        "stats": "📚 You have {n} games ({plats}). You've finished {done}, roughly {hours:,.0f} hours in total. {later} games are waiting on your Play Later list.",
        "later_empty": "Your Play Later list is empty. Tap the ☆ on any card to add one.",
        "later": "⭐ On your Play Later list: {names}{more}. Say 'pick from my list' and I'll choose one.",
        "later_more": " and {n} more",
        "later_pick": "⭐ Picked from your list: {title}. Go!",
        "dur_guest": "Defaults: short ≤ {s:.0f} h, medium ≤ {m:.0f} h, anything above is long. You can customise these after signing up.",
        "dur": "⏱ For you: short ≤ {s:g} h, medium ≤ {m:g} h, above that is long. Change it in Settings → My time preferences.",
        "steam": "Steam: Settings → Platform connections → 'Connect Steam'. You sign in on Steam's own page and your library imports in the background when you're back. Note: 'Game details' on your Steam profile must be Public.",
        "epic": "Epic: 'Connect Epic Games' opens the Epic login in a new tab. After signing in you'll see text containing 'authorizationCode'; paste it into the box under the card and hit 'Connect and import'. The code is single-use.",
        "gog": "GOG: after 'Connect GOG', sign in; then copy the full address from the address bar (embed.gog.com/on_login_success?...code=...) and paste it into the box. The code is valid for about a minute.",
        "manual": "Platforms like {list} don't allow third-party sign-in. Add those games via My Library → '＋ Add game': search RAWG, pick the platform; badges and recommendations work the same way.",
        "conn_none": "No platforms connected yet. Connect Steam, Epic or GOG from Settings → Platform connections.",
        "conn_auto": "connected accounts: {x}", "conn_manual": "added manually: {x}",
        "help": "You can ask:\n• 'recommend a game' / 'recommend a short game' — random pick from your library\n• 'how many games do I have' — library summary\n• 'my play later list' / 'pick from my list'\n• 'how do I connect steam' (epic, gog, ubisoft…)\n• 'time settings', 'genres', 'theme'\n• 'contact' — reach the developer",
        "cats": "Genres come from RAWG (Action, RPG, Indie…); a game can belong to several. Pick a genre on the Recommend page to get matches from both your library and RAWG.",
        "theme": "Theme: the colour dots in the avatar menu at the top right, or Settings → Theme. Blend, PlayStation, Netflix and Neon. Language switches from the same menu.",
        "account": "Password reset and account deletion aren't in the UI yet; email {mail} and I'll sort it out.",
        "contact": "If something's wrong, email {mail} — ideally with the page and what you were doing. Quick tip: Ctrl+Shift+R fixes most display glitches.",
        "fallback": ["I didn't quite get that. Say 'recommend a game' and I'll pick from your library.", "I didn't quite get that. Type 'help' to see what I can do.", "I didn't quite get that. Try 'how many games do I have' or 'how do I connect steam'."],
        "guest": "guest",
    },
}


def _norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", text.lower().translate(_TR)).strip() + " "


def _any(text: str, *words: str) -> bool:
    return any(w in text for w in words)


class ChatBot:
    """Kural tabanlı asistan (TR/EN). Giriş yapmış kullanıcı için kütüphanesinden veri okur."""

    def __init__(self, db: Session, user: User | None, lang: str = "tr"):
        self.db = db
        self.user = user
        self.lang = lang if lang in _T else "tr"
        self.m = _T[self.lang]

    def _name(self) -> str:
        return self.user.username if self.user else self.m["guest"]

    def _duration_from(self, t: str) -> str | None:
        if _any(t, "kisa", "hizli", "az vakt", "short", "quick", "half an hour", "an hour"):
            return "short"
        if _any(t, "orta", "medium", "mid"):
            return "medium"
        if _any(t, "uzun", "cok vakt", "bol vakt", "hafta sonu", "long", "weekend", "lots of time"):
            return "long"
        return None

    # ---------- niyetler ----------

    def _suggest(self, t: str) -> str:
        if not self.user:
            return self.m["login"]
        try:
            g = SuggestionService(self.db).get_random_suggestion(self.user.id, None, self._duration_from(t))
        except Exception:
            return self.m["no_lib"]
        hours = self.m["hours"].format(h=g["estimated_hours"]) if g.get("estimated_hours") else ""
        plat = ", ".join(p.capitalize() for p in g.get("platforms", [])) or self.m["lib_word"]
        link = f"\n{g['link']}" if g.get("link") else ""
        return self.m["suggest"].format(title=g["title"], hours=hours, plat=plat, tail=random.choice(self.m["tails"]), link=link)

    def _stats(self) -> str:
        if not self.user:
            return self.m["login"]
        items = SuggestionService(self.db).get_library_overview(self.user.id)
        if not items:
            return self.m["stats_empty"]
        by_plat = Counter(p for it in items for p in it["platforms"])
        plats = ", ".join(f"{p.capitalize()} {n}" for p, n in by_plat.most_common())
        later = len(PlayLaterRepository(self.db).game_ids_for_user(self.user.id))
        return self.m["stats"].format(n=len(items), plats=plats, done=sum(1 for it in items if it["completed"]),
                                      hours=sum(it["estimated_hours"] or 0 for it in items), later=later)

    def _play_later(self) -> str:
        if not self.user:
            return self.m["login"]
        rows = PlayLaterRepository(self.db).list_for_user(self.user.id)
        if not rows:
            return self.m["later_empty"]
        more = self.m["later_more"].format(n=len(rows) - 5) if len(rows) > 5 else ""
        return self.m["later"].format(names=", ".join(r.game.title for r in rows[:5]), more=more)

    def _play_later_pick(self) -> str:
        if not self.user:
            return self.m["login"]
        rows = PlayLaterRepository(self.db).list_for_user(self.user.id)
        if not rows:
            return self.m["later_empty"]
        return self.m["later_pick"].format(title=random.choice(rows).game.title)

    def _durations(self) -> str:
        if not self.user:
            return self.m["dur_guest"].format(s=DEFAULT_SHORT_MAX_HOURS, m=DEFAULT_MEDIUM_MAX_HOURS)
        s = UserSettingsRepository(self.db).get_by_user_id(self.user.id)
        return self.m["dur"].format(s=s.short_max_hours if s else DEFAULT_SHORT_MAX_HOURS, m=s.medium_max_hours if s else DEFAULT_MEDIUM_MAX_HOURS)

    def _platform_help(self, t: str) -> str:
        for key in ("steam", "epic", "gog"):
            if key in t:
                return self.m[key]
        manual = ", ".join(v for k, v in MANUAL_PLATFORMS.items() if k != "other")
        return self.m["manual"].format(list=manual)

    def _connected(self) -> str:
        if not self.user:
            return self.m["login"]
        accs = PlatformAccountRepository(self.db).get_by_user_id(self.user.id)
        if not accs:
            return self.m["conn_none"]
        auto = [a.platform_name.capitalize() for a in accs if a.platform_name in CONNECTORS]
        manual = [MANUAL_PLATFORMS.get(a.platform_name, a.platform_name) for a in accs if a.platform_name in MANUAL_PLATFORMS]
        parts = ([self.m["conn_auto"].format(x=", ".join(auto))] if auto else []) + ([self.m["conn_manual"].format(x=", ".join(manual))] if manual else [])
        return "🔗 " + "; ".join(parts).capitalize() + "."

    # ---------- ana giriş ----------

    def reply(self, raw: str) -> str:
        t = _norm(raw)
        m = self.m
        if not t.strip():
            return m["empty"]
        if _any(t, "yardim", "help", "neler yapabilirsin", "komut", "ne sorabilirim", "what can you do"):
            return m["help"]
        if _any(t, "tesekkur", "sagol", "eyvallah", "thanks", "thank you", "cheers"):
            return random.choice(m["thanks"])
        if re.fullmatch(r" (selam|merhaba|hey|hi|hello|sa|slm|yo|iyi (gunler|aksamlar)|gunaydin|good (morning|evening|afternoon))[!. ]* ", t):
            return m["hello"].format(name=self._name())
        if _any(t, "listemden oner", "listemden sec", "sonra oyna listemden", "pick from my list", "from my list", "choose from my list"):
            return self._play_later_pick()
        if _any(t, "sonra oyna", "listem", "yer imi", "kaydettigim", "play later", "my list", "watchlist", "starred"):
            return self._play_later()
        if _any(t, "kac oyun", "kutuphanem", "istatistik", "ozet", "toplam", "how many games", "my library", "stats", "summary"):
            return self._stats()
        if _any(t, "bagli", "hangi platform", "hesaplarim", "connected", "which platform", "my accounts"):
            return self._connected()
        if _any(t, "nasil bagla", "bagla", "ice aktar", "import", "connect", "steam", "epic", "gog", "ubisoft", "rockstar", "battle", "xbox", "playstation", "nintendo", " ea "):
            return self._platform_help(t)
        if _any(t, " sure", "kac saat", "kisa oyun ne", "esik", "time setting", "how many hours", "threshold", "duration"):
            return self._durations()
        if _any(t, "kategori", " tur ", "genre", "category", "categories"):
            return m["cats"]
        if _any(t, "tema", "renk", "karanlik", "theme", "colour", "color", "dark mode", " dil ", "language"):
            return m["theme"]
        if _any(t, "sifre", "parola", "hesabimi sil", "e-posta degis", "password", "delete my account", "change email"):
            return m["account"].format(mail=CONTACT_EMAIL)
        if _any(t, "iletisim", "gelistirici", "admin", "hata", "bug", "calismiyor", "sorun", "contact", "developer", "error", "broken", "not working", "issue"):
            return m["contact"].format(mail=CONTACT_EMAIL)
        if _any(t, "oner", "ne oynasam", "ne oynayayim", "rastgele", " sec", "oyun bul", "sikildim", "canim", "recommend", "suggest", "what should i play", "random", "pick", "bored"):
            return self._suggest(t)
        return random.choice(m["fallback"])
