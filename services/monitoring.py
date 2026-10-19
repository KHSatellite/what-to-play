import sentry_sdk
from config import settings


def init_sentry() -> None:
    if not settings.sentry_dsn:
        print("[sentry] SENTRY_DSN tanımlı değil, hata izleme devre dışı.")
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=1.0,
    )
    print(f"[sentry] Aktif, environment='{settings.environment}'")
