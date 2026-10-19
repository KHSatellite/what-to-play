# What to Play — Ne Oynasam? 🎮

> **"Yüzlerce oyun, sıfır karar."** Steam, Epic Games ve GOG kütüphanelerini tek yerde toplayan, ne kadar vaktin olduğuna ve hangi türde oynamak istediğine göre oyun öneren full-stack web uygulaması.

*Kütüphanesinde yüzlerce oyun olup "bugün ne oynasam?" diye 20 dakika launcher'lar arasında gezinen herkes için yazıldı — en başta kendim için.*

**Stack:** FastAPI · SQLAlchemy 2 · PostgreSQL · Redis · RabbitMQ · React 18 · Vite · Framer Motion · Docker Compose

---

## İçindekiler

1. [Neler yapıyor?](#neler-yapıyor)
2. [Mimari](#mimari)
3. [Öne çıkan teknik kararlar](#öne-çıkan-teknik-kararlar)
4. [Kurulum](#kurulum)
5. [Ortam değişkenleri ve gizli bilgiler](#ortam-değişkenleri-ve-gizli-bilgiler)
6. [API özeti](#api-özeti)
7. [Proje yapısı](#proje-yapısı)
8. [Test](#test)
9. [Yol haritası](#yol-haritası)

---

## Neler yapıyor?

**Platform entegrasyonu**
- **Steam** — OpenID ile giriş, resmi Web API'den kütüphane (`GetOwnedGames`).
- **Epic Games** — Launcher OAuth akışı (authorization code), `assets` endpoint'inden yalnızca yüklenebilir oyunlar; DLC / Unreal varlıkları / tekrar eden entitlement'lar filtrelenir.
- **GOG** — Galaxy OAuth akışı, sayfalı kütüphane listesi.
- **Ubisoft, EA, Rockstar, Battle.net, Xbox, PlayStation, Nintendo** — üçüncü taraf girişine izin vermeyen platformlar için RAWG araması ile tek tek ekleme; rozet ve öneri akışı aynı.
- Her platform `services/platforms/` altında tek bir *connector* sınıfı; yeni platform eklemek = bir sınıf + bir kayıt satırı.

**Kütüphane içe aktarma**
- Her oyun RAWG veritabanıyla eşleştirilir (tür, süre, kapak). Eşleştirme sürüm eklerini ("Deluxe / Ultimate / GOTY Edition"), tire varyantlarını ve ™/® işaretlerini normalize eder.
- RAWG aramaları `ThreadPoolExecutor` ile paralel, veritabanı yazımı tek session'da sıralı → 370 oyunluk kütüphane ~30 sn.
- Bellek içi ilerleme takibi (`import_progress`) ve arayüzde canlı ilerleme çubuğu; atlanan oyunlar listelenir.
- Aynı oyun birden fazla platformdaysa tek kart, platform başına renkli rozet.

**Öneri motoru**
- 20 öneri, sabit kotayla: **Steam %50, RAWG %25, diğer kütüphane platformları %25'i paylaşır**. Bir kaynakta yeterli oyun yoksa açık sırayla diğerlerine geçer, RAWG hiçbir zaman kütüphane doluyken payını aşmaz.
- Filtreler: kategori (many-to-many, RAWG türleri) ve süre (kullanıcıya özel "kısa / orta / uzun" eşikleri).
- RAWG önerileri kullanıcının zaten sahip olduğu oyunları dışlar.
- İki tür rastgele: filtresiz tam rastgele ve sonuçlar arasından "rulet" animasyonlu seçim.

**Kullanıcı deneyimi**
- **Sonra Oyna** listesi (watch-later mantığı): kütüphane oyunları ve henüz sahip olunmayan RAWG önerileri aynı listede.
- **Sohbet asistanı** — WebSocket üzerinden kural tabanlı bot; kullanıcının verisine göre yanıt verir ("kısa bir oyun öner", "kaç oyunum var", "GOG nasıl bağlanır").
- 4 tema (Karışım / PlayStation / Netflix / Neon), scroll'a bağlı 3D oyun kutusu animasyonu, sayfa geçişleri (Framer Motion).
- JWT kimlik doğrulama, rol/izin tabanlı yetkilendirme (Redis önbellekli), kayıt sonrası RabbitMQ kuyruğu üzerinden hoş geldin e-postası, Accept-Language'a göre yerelleştirilmiş hata mesajları, Sentry entegrasyonu.

---

## Mimari

```
┌──────────────┐   HTTPS / WS    ┌───────────────────────────────────────────────┐
│ React (Vite) │ ◄─────────────► │ FastAPI                                        │
│ SPA, static/ │                 │  routers → services → repositories → SQLAlchemy│
└──────────────┘                 │        │                                       │
                                 │        ├─ services/platforms/ (Steam/Epic/GOG) │
                                 │        ├─ RawgClient (httpx, retry, pool)      │
                                 │        ├─ chat_bot (WebSocket)                 │
                                 │        └─ email_queue ──► RabbitMQ ──► worker  │
                                 └───────┬───────────────┬───────────────────────┘
                                         │               │
                                    PostgreSQL         Redis (izin önbelleği)
```

**Katmanlar**

| Katman | Sorumluluk | Örnek |
|---|---|---|
| `routers/` | HTTP/WS sözleşmesi, doğrulama, kimlik | `platform_accounts.py`, `chat.py` |
| `services/` | İş kuralları; dış servisler burada soyutlanır | `SuggestionService`, `PlatformAccountService` |
| `repositories/` | Sorgular; ORM detayları servislerden gizli | `GameRepository.get_suggestions` |
| `models/` | SQLAlchemy modelleri | `Game ⇄ Category` (many-to-many), `LibraryEntry`, `PlayLater` |
| `frontend/src/` | React sayfaları, context'ler (auth / tema / sonra-oyna) | `pages/Recommend.jsx`, `playLater.jsx` |

**Veri modeli (özet)**

```
User ──< PlatformAccount ──< LibraryEntry >── Game >──< Category
  │                                             │
  └──< UserSettings                             └──< PlayLater >── User
```

---

## Öne çıkan teknik kararlar

Bunlar projede karşılaştığım gerçek sorunlar ve verdiğim kararlar; kod incelemesinde nereye bakılacağını gösterir.

- **ORM nesnelerini önbelleğe koymamak.** İlk sürümde repository katmanı SQLAlchemy nesnelerini süreç içi TTL cache'e yazıyordu; farklı request'lerin session'ları arasında *"already attached to session"* hataları üretti. Cache tamamen kaldırıldı — Postgres'te PK sorgusu mikrosaniyeler sürüyor, cache'in faydası yoktu, zararı vardı (KISS/YAGNI).
- **Ağ işini paralel, DB işini sıralı yapmak.** SQLAlchemy session'ı thread-safe değil. İçe aktarmada RAWG aramaları (`GameService.lookup_rawg`, saf ağ) thread havuzunda, veritabanı yazımı (`upsert_from_rawg`) tek thread'de. Bu ayrım aynı zamanda `GameService`'in sorumluluklarını netleştirdi.
- **Uzun işleri request'in dışına almak.** Steam callback'i yüzlerce RAWG çağrısını senkron yapıyor, tarayıcı bağlantıyı kesip yönlendirme hiç tamamlanmıyordu. Import `BackgroundTasks`'e taşındı; arayüz ilerlemeyi endpoint'ten okuyor.
- **Strateji deseni ile platform bağlayıcıları.** `PlatformConnector` arayüzü (`exchange_code`, `fetch_games`); Steam redirect, Epic/GOG kod tabanlı. `PlatformAccountService` hangi platformla konuştuğunu bilmez (Open/Closed).
- **Öneri dağılımını açıkça modellemek.** Eşit round-robin, kütüphanesi küçük platformların önerileri domine etmesine yol açtı; kota + sıralı açık kapatma (`SuggestionService._allocate`) ürünün "önce senin kütüphanen" ilkesini koda yazıyor.
- **Frontend'de çıkış animasyonundan vazgeçmek.** `AnimatePresence`, çıkış animasyonu sırasında ağaç yeniden render olursa (login/logout tam da bunu yapar) takılıyor ve yeni sayfa hiç mount olmuyordu. Yalnızca giriş animasyonu kaldı; yönlendirmeler `<Navigate>` yerine tek seferlik, rota-korumalı bir effect ile yapılıyor.
- **`position: fixed` ve transform tuzağı.** Animasyonlu sayfa sarmalayıcısı `transform/filter` bıraktığında modal sayfanın içine hapsoluyordu; modal `createPortal` ile `body`'ye taşındı.
- **Gizli bilgiler koda girmez.** Tüm anahtarlar `.env`'de (`pydantic-settings`), `.env.example` şablon; platform token'ları veritabanında JSON olarak tutulur ve API yanıtlarına asla yazılmaz.

---

## Kurulum

**Gereksinimler:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker. (Node.js 18+ sadece frontend'i geliştirmek için.)

```bash
git clone https://github.com/KHSatellite/what-to-play.git
cd what-to-play

cp .env.example .env            # değerleri doldur (aşağıya bak)
docker compose up -d            # PostgreSQL, Redis, RabbitMQ
uv sync                         # Python bağımlılıkları

uv run uvicorn main:app --reload
```

`http://localhost:8000` adresinde uygulama açılır. Tablolar ilk açılışta oluşturulur, kategoriler RAWG'dan çekilir.

> `static/` klasöründe frontend'in hazır build'i repoyla birlikte gelir, FastAPI onu doğrudan servis eder. Node.js yalnızca arayüz kodunu değiştirirsen gerekir; değişiklikten sonra `cd frontend && npm install && npm run build` ile `static/` yeniden üretilir.

**Frontend üzerinde çalışırken**

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, API çağrıları 8000'e proxy'lenir
```

**İsteğe bağlı servisler**

```bash
uv run python worker.py                   # hoş geldin e-postası kuyruğunu dinler
uv run python seed_admin.py <kullanıcı>   # superadmin rolü + manage_roles izni
```

---

## Ortam değişkenleri ve gizli bilgiler

Tüm anahtarlar ve şifreler yalnızca `.env` dosyasında tutulur. `.env` git'e girmez; repoda sadece boş şablon olan `.env.example` bulunur. Yeni bir anahtar eklediğinde şablona da değeri boş olarak ekle.

| Değişken | Zorunlu | Açıklama |
|---|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, `DB_PORT` | ✔ | PostgreSQL bağlantısı |
| `RAWG_API_KEY` | ✔ | [rawg.io/apidocs](https://rawg.io/apidocs) — ücretsiz |
| `STEAM_API_KEY` | ✔ (Steam için) | [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey) |
| `SECRET_KEY` | ✔ | JWT imzası, `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | Varsayılan 30; 1440 önerilir |
| `REDIS_HOST/PORT`, `RABBITMQ_HOST/PORT` | | docker-compose varsayılanları |
| `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD` | | Boşsa e-posta atlanır. Normal Gmail şifresi değil, [uygulama şifresi](https://myaccount.google.com/apppasswords) kullanılır |
| `SENTRY_DSN`, `ENVIRONMENT` | | Boşsa hata izleme kapalı |

Epic ve GOG için ek anahtar gerekmez; açık kaynak launcher'ların (Legendary, Heroic) kullandığı herkese açık istemci kimlikleri kullanılır.

---

## API özeti

Tam dokümantasyon: `http://localhost:8000/docs` (Swagger).

| Yöntem | Yol | Açıklama |
|---|---|---|
| `POST` | `/users/` · `/auth/token` | Kayıt, giriş (OAuth2 password flow, JWT) |
| `GET` | `/users/me` | Oturumdaki kullanıcı |
| `GET/PUT` | `/users/{id}/settings` | Kısa/orta süre eşikleri |
| `GET` | `/users/{id}/library-overview` | Oyun bazında gruplu kütüphane (platformlar, kategoriler) |
| `GET` | `/users/{id}/suggestions/combined` | 20 öneri (`category_id`, `duration`) |
| `GET` | `/users/{id}/suggestions/random` | Filtreli/filtresiz rastgele |
| `GET` | `/platform-accounts/connectors` | Bağlayıcılar + bağlı hesaplar |
| `GET` | `/platform-accounts/steam/login` → `/callback` | Steam OpenID |
| `POST` | `/platform-accounts/connect-code` | Epic / GOG yetki kodu |
| `POST` | `/platform-accounts/{id}/import` · `GET …/import-status` | İçe aktarma + ilerleme |
| `GET/POST` | `/platform-accounts/rawg-search` · `/manual-add` | Elle ekleme |
| `GET/POST/DELETE` | `/play-later/` | Sonra Oyna listesi |
| `GET` | `/public/showcase` | Ana sayfa vitrini (auth yok, 5 dk cache) |
| `WS` | `/ws/chat?token=` | Sohbet asistanı |
| `GET/POST` | `/roles/`, `/users/{id}/roles/{role_id}` | RBAC (izin gerektirir) |

---

## Proje yapısı

```
.
├── main.py                  # uygulama, SPA fallback, startup (kategori senkronu)
├── config.py                # pydantic-settings
├── database.py              # engine, session
├── models/                  # SQLAlchemy modelleri
├── repositories/            # sorgu katmanı (BaseRepository generic)
├── services/
│   ├── game_service.py      # GameService (CRUD, RAWG eşleştirme) + SuggestionService
│   ├── platform_account_service.py
│   ├── platforms/           # base.py, steam.py, epic.py, gog.py
│   ├── play_later_service.py
│   ├── chat_bot.py          # kural tabanlı asistan
│   ├── rawg_client.py       # httpx client, retry, backoff
│   ├── import_progress.py
│   ├── token_service.py · authorization_service.py · permission_cache.py
│   └── email_queue.py · rabbitmq_client.py · email_service.py
├── routers/                 # auth, users, games, categories, platform_accounts, steam_auth, play_later, chat, public, roles
├── locales/                 # tr / en mesajlar
├── worker.py                # RabbitMQ tüketicisi
├── seed_admin.py
├── frontend/                # Vite + React kaynakları
│   └── src/{pages,components}, api.js, auth.jsx, theme.jsx, playLater.jsx
├── static/                  # frontend'in hazır build çıktısı (npm run build üretir)
├── docker-compose.yml       # postgres, redis, rabbitmq
├── .env.example             # ortam değişkeni şablonu
└── test_*.py                # akış testleri
```

---

## Test

Test betikleri çalışan bir sunucuya istek atar. Önce `uv run uvicorn main:app` ile sunucuyu başlat, sonra ayrı bir terminalde:

```bash
uv run python test_flow.py          # kayıt → giriş → ayarlar → öneri
uv run python test_auth_flow.py
uv run python test_authorization.py
uv run python test_new_features.py
```

Platform bağlayıcıları ve öneri dağılımı geliştirme sırasında `httpx.MockTransport` ile sahte Epic/GOG/RAWG yanıtları üzerinden doğrulandı; frontend akışları (giriş → panel → öneri → sonra oyna → çıkış) Playwright ile uçtan uca test edildi.

---

## Yol haritası

- [ ] Steam giriş endpoint'inde imzalı `state` (CSRF)
- [ ] Şifre sıfırlama ve hesap silme
- [ ] Xbox (OpenXBL) ve PlayStation (npsso) bağlayıcıları
- [ ] Alembic ile migrasyon
- [ ] Docker imajı (backend + build edilmiş frontend)

---

**Geliştirici:** Kadir Hanbaba · [github.com/KHSatellite](https://github.com/KHSatellite) · hanbaba.kadir8@gmail.com
Oyun verileri [RAWG](https://rawg.io) ve platformların kendi API'lerinden alınır.
