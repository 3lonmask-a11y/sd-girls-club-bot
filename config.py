# config.py
import os
from dataclasses import dataclass, field
from typing import Tuple, List

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip() or default)
    except ValueError:
        return default

def _env_tuple_int(name: str, default: Tuple[int, ...]) -> Tuple[int, ...]:
    raw = os.getenv(name, "")
    if not raw:
        return default
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    out: List[int] = []
    for p in parts:
        try:
            out.append(int(p))
        except ValueError:
            continue
    return tuple(out) or default

@dataclass
class Settings:
    # === БАЗОВОЕ ===
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")  # обязательно в Environment
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")
    DATA_FILE: str = os.getenv("DATA_FILE", "data/users.json")

    # === АДМИНЫ / ЧАТ ДЛЯ УВЕДОМЛЕНИЙ ===
    ADMINS: Tuple[int, ...] = _env_tuple_int("ADMINS", (931831277,))
    ADMIN_CHAT_ID: int = _env_int("ADMIN_CHAT_ID", 931831277)

    # === ПОДПИСКА ===
    SUBSCRIPTION_PRICE: int = _env_int("SUBSCRIPTION_PRICE", 590)
    SUBSCRIPTION_DAYS: int = _env_int("SUBSCRIPTION_DAYS", 30)

    # === ССЫЛКИ (можешь оставить пустыми, если не нужны) ===
    SUBSCRIPTION_LINK: str = os.getenv("SUBSCRIPTION_LINK", "")
    MATERIALS_LINK: str = os.getenv("MATERIALS_LINK", "")
    SEASONS_LINK: str = os.getenv("SEASONS_LINK", "")
    CLUB_CHANNEL_LINK: str = os.getenv("CLUB_CHANNEL_LINK", "")
    CLUB_CHAT_LINK: str = os.getenv("CLUB_CHAT_LINK", "")
    GIFT_SUBSCRIPTION_LINK: str = os.getenv("GIFT_SUBSCRIPTION_LINK", "")

    # === РЕКВИЗИТЫ ДЛЯ РУЧНОЙ ОПЛАТЫ ===
    PAYEE_NAME: str = os.getenv("PAYEE_NAME", "Имя Фамилия")
    PAYEE_BANK: str = os.getenv("PAYEE_BANK", "Банк")
    PAYEE_ACCOUNT: str = os.getenv("PAYEE_ACCOUNT", "XXXX XXXX XXXX XXXX")

    # === КАРТИНКИ ДЛЯ «Архив знаний» (опционально) ===
    ARCHIVE_PHOTOS: List[str] = field(default_factory=list)
    # Пример: в Environment: ARCHIVE_PHOTOS="https://…1.jpg,https://…2.jpg"
    def __post_init__(self):
        raw = os.getenv("ARCHIVE_PHOTOS", "")
        if raw:
            self.ARCHIVE_PHOTOS = [u.strip() for u in raw.split(",") if u.strip()]

settings = Settings()


