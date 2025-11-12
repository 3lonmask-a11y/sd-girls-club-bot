# config.py
import os
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMINS: Tuple[int, ...] = tuple(map(int, os.getenv("ADMINS", "931831277").split(",")))
    ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "931831277"))

    CLUB_CHANNEL_LINK: str = os.getenv("CLUB_CHANNEL_LINK", "")
    CLUB_CHAT_LINK: str = os.getenv("CLUB_CHAT_LINK", "")
    MATERIALS_LINK: str = os.getenv("MATERIALS_LINK", "")
    SEASONS_LINK: str = os.getenv("SEASONS_LINK", "")

    SUBSCRIPTION_DAYS: int = int(os.getenv("SUBSCRIPTION_DAYS", "30"))
    SUBSCRIPTION_PRICE: int = int(os.getenv("SUBSCRIPTION_PRICE", "590"))

    PAYEE_NAME: str = os.getenv("PAYEE_NAME", "")
    PAYEE_BANK: str = os.getenv("PAYEE_BANK", "")
    PAYEE_ACCOUNT: str = os.getenv("PAYEE_ACCOUNT", "")

    TIMEZONE: str = "Europe/Moscow"
    DATA_FILE: str = "data/users.json"

    ARCHIVE_PHOTOS: List[str] = os.getenv("ARCHIVE_PHOTOS", "").split(",") if os.getenv("ARCHIVE_PHOTOS") else []
    ARCHIVE_CAPTION: str = os.getenv("ARCHIVE_CAPTION", "Гайды, чек-листы и шпаргалки. Обновляем регулярно.")

settings = Settings()

