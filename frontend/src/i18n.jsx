import { createContext, useContext, useEffect, useState } from 'react'

export const LANGS = [
  { id: 'tr', name: 'Türkçe', flag: '🇹🇷' },
  { id: 'en', name: 'English', flag: '🇬🇧' },
]
const KEY = 'ne_oynasam_lang'

const tr = {
  // genel
  brand_sub: 'Kütüphanende ne oynayacağına karar veremediğinde buradayız.',
  nav_panel: 'Panel', nav_recommend: 'Oyun Öner', nav_library: 'Kütüphanem', nav_later: 'Sonra Oyna',
  nav_login: 'Giriş', nav_register: 'Kayıt Ol', nav_settings: 'Ayarlar', nav_logout: 'Çıkış Yap', theme: 'Tema', language: 'Dil',
  footer_contact: 'İletişim', footer_sources: 'Kaynaklar', footer_rawg: 'RAWG veritabanı', footer_note: 'Oyun verileri RAWG ve Steam\'den alınır.',
  loading: 'Yükleniyor…', save: 'Kaydet', saved: 'Kaydedildi ✓', error_generic: 'Bir hata oluştu.', back: 'Geri', cancel: 'Vazgeç', close: 'Kapat',
  hours_approx: '~{h} saat', hours_unknown: 'Süre bilinmiyor', open: 'Aç ↗', play_or_view: 'Oyna / İncele',
  badge_rawg: 'RAWG önerisi', in_library: 'Kütüphanende', not_in_library: 'Henüz kütüphanende değil',
  // landing
  hero_eyebrow: 'Steam · Epic · GOG + RAWG destekli öneri motoru', hero_title_1: 'Bugün', hero_title_2: 'ne oynasam?',
  hero_lead: 'Yüzlerce oyun, sıfır karar. Vaktini ve modunu söyle, kütüphanenden ya da dünyadan sana en uygun 20 oyunu getirelim.',
  hero_cta_user: 'Öneri al', hero_cta_guest: 'Hemen başla', hero_how: 'Nasıl çalışır?',
  showcase_title: 'Şu an popüler', showcase_sub: 'RAWG\'dan canlı çekilen vitrin', steps_title: 'Üç adımda karar',
  step1_t: 'Platformlarını bağla', step1_d: 'Steam, Epic Games ve GOG hesaplarınla giriş yap; kütüphanelerin arka planda otomatik içe aktarılsın.',
  step2_t: 'Süre ve kategori seç', step2_d: 'Bugün ne kadar vaktin var? Hangi türde oynamak istiyorsun? İki soru, o kadar.',
  step3_t: 'Oyununu al', step3_d: '20 öneri: Steam, Epic, GOG kütüphanelerinden ve RAWG\'dan dengeli. Kararsızsan rastgele seçtir.',
  features_title: 'Neler var?',
  f1_t: 'Kütüphane analizi', f1_d: 'Sahip olduğun ama hiç açmadığın oyunları süre ve türe göre sınıflandırır.',
  f2_t: 'RAWG ile tamamlama', f2_d: 'Kütüphanende yeterince oyun yoksa, sahip olmadıklarını en yüksek puanlılardan önerir.',
  f3_t: 'İki tür rastgele', f3_d: 'Tamamen rastgele ya da filtrelediğin sonuçlar arasından — kararsızlık bitiyor.',
  f4_t: 'Kişisel süre eşikleri', f4_d: '"Kısa" ve "orta" sana göre ne demek? Ayarlardan kendin belirle.',
  stat_games: 'Oyun veritabanında', stat_categories: 'Kategori', stat_users: 'Kullanıcı',
  cta_title: 'Karar vermeyi bırak, oynamaya başla.', cta_guest: 'Ücretsiz kayıt ol',
  // auth
  login_title: 'Tekrar hoş geldin', login_sub: 'Kütüphanen seni bekliyor.', username: 'Kullanıcı adı', password: 'Şifre', email: 'E-posta',
  login_btn: 'Giriş yap', login_busy: 'Giriş yapılıyor…', login_fail: 'Giriş başarısız', expired: 'Oturum süren doldu, tekrar giriş yap.',
  no_account: 'Hesabın yok mu?', have_account: 'Zaten hesabın var mı?',
  register_title: 'Aramıza katıl', register_sub: 'Bir dakikadan kısa sürer.', continue: 'Devam', pw_min: 'Şifre en az 8 karakter olmalı',
  register_step2_title: 'Süre tercihin', register_step2_sub: '"Kısa" ve "orta" oyun senin için kaç saat? Sonra değiştirebilirsin.',
  short_max: 'Kısa oyun üst sınırı (saat)', medium_max: 'Orta oyun üst sınırı (saat)', create_account: 'Hesabı oluştur', creating: 'Oluşturuluyor…', register_fail: 'Kayıt başarısız',
  // dashboard
  greet_night: 'İyi geceler', greet_morning: 'Günaydın', greet_day: 'İyi günler', greet_evening: 'İyi akşamlar',
  tile_games: 'Oyun', tile_waiting: 'Oynanmayı bekleyen', tile_done: 'Bitirilen', tile_hours: 'Tahmini saat',
  act_recommend_t: 'Öneri al', act_recommend_d: 'Süre ve kategori seç, 20 oyun gelsin.',
  act_later_t: 'Sonra oyna', act_later_d_n: '{n} oyun seni bekliyor.', act_later_d_0: 'Beğendiğin oyunları ★ ile işaretle.',
  act_connect_t: 'Platform bağla', act_connect_d: 'Steam, Epic ya da GOG kütüphaneni içe aktar.',
  act_library_t: 'Kütüphanem', act_library_d: '{n} oyunu incele.', shelf_title: 'Rafta bekleyenler', all_arrow: 'Tümü →',
  // recommend
  rec_title_1: 'Ne', rec_title_2: 'oynasam?', rec_time: 'Ne kadar vaktin var?', rec_category: 'Kategori', all: 'Tümü',
  dur_any: 'Farketmez', dur_short: 'Kısa', dur_medium: 'Orta', dur_long: 'Uzun',
  rec_btn: 'Öneri getir', rec_busy: 'Aranıyor…', rec_random: '🎲 Tamamen rastgele', rec_random_title: 'Süre ve kategoriden bağımsız, kütüphanenden rastgele',
  rec_count: '{n} öneri', rec_none: 'Sonuç yok', rec_none_hint: 'Bu kriterlere uyan oyun bulunamadı. Filtreleri gevşetmeyi dene.',
  rec_pick: '🎯 Kararsızım, sen seç', rec_no_library: 'Kütüphanende oynanmamış oyun bulunamadı. Önce bir platform bağla.', cats_fail: 'Kategoriler yüklenemedi',
  mode_random: 'Tamamen rastgele', mode_from_results: 'Sonuçlar arasından', mode_from_list: 'Listenden rastgele', pick: 'Seçim',
  spin_again: 'Bir daha çevir', pick_again: 'Tekrar seç', again: 'Bir daha', approx_hours: 'Yaklaşık {h} saat',
  // library
  lib_title: 'Kütüphanem', lib_count: '{a} / {b} oyun', add_game: '＋ Oyun ekle', search_game: 'Oyun ara…', all_platforms: 'Tüm platformlar', all_categories: 'Tüm kategoriler',
  filt_all: 'Hepsi', filt_todo: 'Oynanacak', filt_done: 'Bitirildi', mark_done: 'Bitirdim', undo_done: 'Bitirmedim', is_done: '✓ Bitirildi', remove: 'Kaldır',
  remove_confirm: '{title} kütüphanenden ({p}) kaldırılsın mı?',
  lib_empty_t: 'Kütüphanen boş', lib_empty_d: 'Bir platform bağlayınca ya da oyun ekleyince burada görünecek.', connect_platform: 'Platform bağla', add_game_plain: 'Oyun ekle',
  add_title: 'Oyun ekle', add_sub: 'Giriş desteği olmayan platformlar için: oyunu RAWG\'da bul, platformunu seç, ekle.', add_placeholder: 'Oyun adı yaz…', add_btn: 'Ekle', added: '{title} eklendi ✓', no_results: 'Sonuç yok.',
  // play later
  later_title_1: 'Sonra', later_title_2: 'oyna', later_sub: 'Öneri ve kütüphane kartlarındaki ★ ile buraya eklediğin oyunlar. Hem kütüphanendekiler hem RAWG önerileri olabilir.',
  later_random: '🎲 Listeden rastgele', later_empty_t: 'Listen boş', later_empty_d: 'Bir kartın köşesindeki ☆ simgesine dokun, buraya düşsün.',
  pl_add: 'Sonra oyna listesine ekle', pl_remove: 'Sonra oyna listesinden çıkar', pl_in: 'Listede', pl_label: 'Sonra oyna',
  // settings
  settings_title: 'Ayarlar', plat_title: 'Platform bağlantıları', plat_sub: 'Bağladığın her platformun kütüphanesi otomatik içe aktarılır; önerilerde hangi platformdan geldiği görünür.',
  connected: 'Bağlı', last_sync: 'Son senkron {d}', not_imported: 'Henüz içe aktarılmadı', reconnect: 'Yeniden bağla', connect_with: '{p} ile bağlan', reimport: 'Yeniden içe aktar',
  remove_platform_confirm: '{p} bağlantısı ve bu platformdan gelen oyunlar kütüphanenden kaldırılacak. Emin misin?',
  code_hint_link: 'Sekme açılmadıysa:', login_page: 'giriş sayfası', code_placeholder: 'Kodu ya da tüm metni buraya yapıştır', connect_import: 'Bağla ve içe aktar', verifying: 'Doğrulanıyor…',
  imp_done: 'Tamamlandı · platformda {t} oyun: {i} yeni eklendi, {a} zaten vardı, {s} eşleşmedi', imp_dups: ', {d} tekrar', imp_running: '{d} / {t} yeni oyun işleniyor',
  imp_skipped: 'Atlananlar ({n}) — RAWG\'da eşleşme bulunamadı', imp_skipped_hint: 'Bunları Kütüphanem → Oyun ekle ile elle ekleyebilirsin.',
  steam_err: 'Steam doğrulaması başarısız oldu, tekrar dene.', steam_ok: 'Steam bağlandı! Kütüphanen arka planda içe aktarılıyor…', connected_importing: '{p} bağlandı, kütüphane içe aktarılıyor…',
  manual_title: 'Ubisoft, EA, Rockstar, Battle.net, Xbox, PlayStation…', manual_d1: 'Bu platformlar üçüncü taraf girişine ve kütüphane dışa aktarımına izin vermiyor. Oyunları', manual_link: 'Kütüphanem → Oyun ekle', manual_d2: 'ile RAWG\'dan arayıp platform seçerek ekleyebilirsin; rozetleri ve önerileri aynı şekilde çalışır.',
  dur_title: 'Süre tercihlerim', dur_sub: '"Kısa" ve "orta" oyunun senin için kaç saat olduğunu belirle.', short_limit: 'Kısa üst sınırı (saat)', medium_limit: 'Orta üst sınırı (saat)',
  theme_title: 'Tema', lang_title: 'Dil', account_title: 'Hesap',
  theme_mix: 'Karışım', theme_mix_d: 'Koyu zemin, cam kartlar, mor-cyan vurgu', theme_ps: 'PlayStation', theme_ps_d: 'Lacivert gradyan, mavi ışık, cam efekti',
  theme_nf: 'Netflix', theme_nf_d: 'Tam siyah, kırmızı vurgu, düz kartlar', theme_neon: 'Neon', theme_neon_d: 'Cyberpunk, pembe-cyan glow',
  // chat
  chat_title: 'Ne Oynasam Asistanı', chat_hello: 'Merhaba {name}', chat_guest: 'Misafir olarak sohbet ediyorsun', chat_fast: 'genelde anında yanıt', chat_placeholder: 'Bir şey sor…', send: 'Gönder',
  chat_q1: 'Oyun öner', chat_q2: 'Kısa bir oyun öner', chat_q3: 'Kaç oyunum var?', chat_q4: 'Steam nasıl bağlanır?', chat_q5: 'Yardım',
}

const en = {
  brand_sub: 'For when you can\'t decide what to play from your own library.',
  nav_panel: 'Dashboard', nav_recommend: 'Recommend', nav_library: 'My Library', nav_later: 'Play Later',
  nav_login: 'Log in', nav_register: 'Sign up', nav_settings: 'Settings', nav_logout: 'Log out', theme: 'Theme', language: 'Language',
  footer_contact: 'Contact', footer_sources: 'Sources', footer_rawg: 'RAWG database', footer_note: 'Game data comes from RAWG and Steam.',
  loading: 'Loading…', save: 'Save', saved: 'Saved ✓', error_generic: 'Something went wrong.', back: 'Back', cancel: 'Cancel', close: 'Close',
  hours_approx: '~{h} h', hours_unknown: 'Unknown length', open: 'Open ↗', play_or_view: 'Play / View',
  badge_rawg: 'RAWG pick', in_library: 'In your library', not_in_library: 'Not in your library yet',
  hero_eyebrow: 'Recommendation engine powered by Steam · Epic · GOG + RAWG', hero_title_1: 'What should I', hero_title_2: 'play today?',
  hero_lead: 'Hundreds of games, zero decisions. Tell us your time and mood and we\'ll pull the 20 best fits from your library or the world.',
  hero_cta_user: 'Get picks', hero_cta_guest: 'Get started', hero_how: 'How it works',
  showcase_title: 'Trending now', showcase_sub: 'Live showcase from RAWG', steps_title: 'Decide in three steps',
  step1_t: 'Connect your platforms', step1_d: 'Sign in with Steam, Epic Games and GOG; your libraries import automatically in the background.',
  step2_t: 'Pick time and genre', step2_d: 'How much time do you have today? What genre are you in the mood for? Two questions, that\'s it.',
  step3_t: 'Get your game', step3_d: '20 picks, balanced across Steam, Epic, GOG and RAWG. Can\'t decide? Let the dice choose.',
  features_title: 'What\'s inside',
  f1_t: 'Library analysis', f1_d: 'Sorts the games you own but never opened by length and genre.',
  f2_t: 'RAWG fill-in', f2_d: 'When your library runs thin, top-rated games you don\'t own fill the gap.',
  f3_t: 'Two kinds of random', f3_d: 'Fully random, or a roulette spin over your filtered results — indecision ends here.',
  f4_t: 'Personal time thresholds', f4_d: 'What "short" and "medium" mean is up to you. Set it in Settings.',
  stat_games: 'Games in database', stat_categories: 'Genres', stat_users: 'Players',
  cta_title: 'Stop deciding. Start playing.', cta_guest: 'Sign up for free',
  login_title: 'Welcome back', login_sub: 'Your library is waiting.', username: 'Username', password: 'Password', email: 'Email',
  login_btn: 'Log in', login_busy: 'Logging in…', login_fail: 'Login failed', expired: 'Your session expired, please log in again.',
  no_account: 'No account yet?', have_account: 'Already have an account?',
  register_title: 'Join us', register_sub: 'Takes less than a minute.', continue: 'Continue', pw_min: 'Password must be at least 8 characters',
  register_step2_title: 'Your time preferences', register_step2_sub: 'How many hours is a "short" or "medium" game for you? You can change this later.',
  short_max: 'Short game upper limit (hours)', medium_max: 'Medium game upper limit (hours)', create_account: 'Create account', creating: 'Creating…', register_fail: 'Sign-up failed',
  greet_night: 'Good night', greet_morning: 'Good morning', greet_day: 'Good afternoon', greet_evening: 'Good evening',
  tile_games: 'Games', tile_waiting: 'Waiting to be played', tile_done: 'Finished', tile_hours: 'Estimated hours',
  act_recommend_t: 'Get picks', act_recommend_d: 'Choose time and genre, get 20 games.',
  act_later_t: 'Play later', act_later_d_n: '{n} games waiting for you.', act_later_d_0: 'Mark games you like with ★.',
  act_connect_t: 'Connect a platform', act_connect_d: 'Import your Steam, Epic or GOG library.',
  act_library_t: 'My library', act_library_d: 'Browse {n} games.', shelf_title: 'On the shelf', all_arrow: 'All →',
  rec_title_1: 'What should I', rec_title_2: 'play?', rec_time: 'How much time do you have?', rec_category: 'Genre', all: 'All',
  dur_any: 'Any', dur_short: 'Short', dur_medium: 'Medium', dur_long: 'Long',
  rec_btn: 'Get picks', rec_busy: 'Searching…', rec_random: '🎲 Fully random', rec_random_title: 'Random from your library, ignoring time and genre',
  rec_count: '{n} picks', rec_none: 'No results', rec_none_hint: 'Nothing matched these filters. Try loosening them.',
  rec_pick: '🎯 Can\'t decide, pick for me', rec_no_library: 'No unplayed games in your library. Connect a platform first.', cats_fail: 'Could not load genres',
  mode_random: 'Fully random', mode_from_results: 'From the results', mode_from_list: 'Random from your list', pick: 'Pick',
  spin_again: 'Spin again', pick_again: 'Pick again', again: 'Again', approx_hours: 'About {h} hours',
  lib_title: 'My Library', lib_count: '{a} / {b} games', add_game: '＋ Add game', search_game: 'Search games…', all_platforms: 'All platforms', all_categories: 'All genres',
  filt_all: 'All', filt_todo: 'To play', filt_done: 'Finished', mark_done: 'Finished it', undo_done: 'Not finished', is_done: '✓ Finished', remove: 'Remove',
  remove_confirm: 'Remove {title} ({p}) from your library?',
  lib_empty_t: 'Your library is empty', lib_empty_d: 'Games appear here once you connect a platform or add one.', connect_platform: 'Connect a platform', add_game_plain: 'Add a game',
  add_title: 'Add a game', add_sub: 'For platforms without sign-in support: find the game on RAWG, choose the platform, add it.', add_placeholder: 'Type a game name…', add_btn: 'Add', added: '{title} added ✓', no_results: 'No results.',
  later_title_1: 'Play', later_title_2: 'later', later_sub: 'Games you starred on recommendation and library cards. Both owned games and RAWG picks can live here.',
  later_random: '🎲 Random from list', later_empty_t: 'Your list is empty', later_empty_d: 'Tap the ☆ in a card\'s corner and it lands here.',
  pl_add: 'Add to play-later list', pl_remove: 'Remove from play-later list', pl_in: 'On the list', pl_label: 'Play later',
  settings_title: 'Settings', plat_title: 'Platform connections', plat_sub: 'Every connected platform\'s library is imported automatically; picks show which platform they came from.',
  connected: 'Connected', last_sync: 'Last sync {d}', not_imported: 'Not imported yet', reconnect: 'Reconnect', connect_with: 'Connect {p}', reimport: 'Re-import',
  remove_platform_confirm: 'This removes the {p} connection and every game imported from it. Are you sure?',
  code_hint_link: 'Tab didn\'t open?', login_page: 'login page', code_placeholder: 'Paste the code or the whole text here', connect_import: 'Connect and import', verifying: 'Verifying…',
  imp_done: 'Done · {t} games on platform: {i} newly added, {a} already there, {s} unmatched', imp_dups: ', {d} duplicates', imp_running: 'Processing {d} / {t} new games',
  imp_skipped: 'Skipped ({n}) — no RAWG match', imp_skipped_hint: 'You can add these manually via My Library → Add game.',
  steam_err: 'Steam verification failed, try again.', steam_ok: 'Steam connected! Your library is importing in the background…', connected_importing: '{p} connected, importing library…',
  manual_title: 'Ubisoft, EA, Rockstar, Battle.net, Xbox, PlayStation…', manual_d1: 'These platforms don\'t allow third-party sign-in or library export. Add games via', manual_link: 'My Library → Add game', manual_d2: 'by searching RAWG and picking the platform; badges and recommendations work the same way.',
  dur_title: 'My time preferences', dur_sub: 'Define how many hours a "short" and a "medium" game is for you.', short_limit: 'Short upper limit (hours)', medium_limit: 'Medium upper limit (hours)',
  theme_title: 'Theme', lang_title: 'Language', account_title: 'Account',
  theme_mix: 'Blend', theme_mix_d: 'Dark base, glass cards, violet-cyan accent', theme_ps: 'PlayStation', theme_ps_d: 'Navy gradient, blue glow, glass',
  theme_nf: 'Netflix', theme_nf_d: 'Pure black, red accent, flat cards', theme_neon: 'Neon', theme_neon_d: 'Cyberpunk, pink-cyan glow',
  chat_title: 'Ne Oynasam Assistant', chat_hello: 'Hi {name}', chat_guest: 'Chatting as a guest', chat_fast: 'usually replies instantly', chat_placeholder: 'Ask something…', send: 'Send',
  chat_q1: 'Recommend a game', chat_q2: 'Recommend a short game', chat_q3: 'How many games do I have?', chat_q4: 'How do I connect Steam?', chat_q5: 'Help',
}

const DICT = { tr, en }
const Ctx = createContext(null)

export const getLang = () => { try { return localStorage.getItem(KEY) || (navigator.language?.startsWith('tr') ? 'tr' : 'en') } catch { return 'tr' } }

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(getLang)
  useEffect(() => {
    try { localStorage.setItem(KEY, lang) } catch { /* yoksay */ }
    document.documentElement.lang = lang
  }, [lang])
  const t = (key, vars) => {
    let s = DICT[lang]?.[key] ?? DICT.tr[key] ?? key
    if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, v)
    return s
  }
  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>
}

export const useT = () => useContext(Ctx)
