import json
from pathlib import Path
from fastapi import Header

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
DEFAULT_LANGUAGE = "en"

_translations: dict[str, dict[str, str]] = {
    path.stem: json.loads(path.read_text(encoding="utf-8-sig"))
    for path in LOCALES_DIR.glob("*.json")
}


def resolve_locale(accept_language: str | None) -> str:
    if accept_language:
        primary = accept_language.split(",")[0].split("-")[0].strip().lower()
        if primary in _translations:
            return primary
    return DEFAULT_LANGUAGE


def get_locale(accept_language: str | None = Header(default=None)) -> str:
    return resolve_locale(accept_language)


def translate(key: str, locale: str) -> str:
    table = _translations.get(locale, _translations[DEFAULT_LANGUAGE])
    return table.get(key, key)
