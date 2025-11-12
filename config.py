# config.py
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class Settings:
    # === ОБЯЗАТЕЛЬНО: токен бота (лучше через переменную окружения BOT_TOKEN на Render) ===
    # Если используешь .env/Environment, можешь оставить пустым тут.
    BOT_TOKEN: str = ""  # оставь пустым, если задаёшь в Render > Environment > BOT_TOKEN

    # === Админские ID (ты и люди, кто подтверждает оплаты) ===
    ADMINS: Tuple[int, ...] = (931831277,)
    ADMIN_CHAT_ID: int = 931831277

    # === Ссылки на твои площадки ===
    CLUB_CHANNEL_LINK: str = "https://t.me/+your_channel"
    CLUB_CHAT_LINK: str = "https://t.me/+your_chat"
    MATERIALS_LINK: str = "https://t.me/+your_materials_or_catalog"
    SEASONS_LINK: str = "https://sedamedia.ru/seasons"

    # === Подписка ===
    SUBSCRIPTION_DAYS: int = 30
    SUBSCRIPTION_PRICE: int = 590  # ₽

    # === Реквизиты (ручная оплата) ===
    PAYEE_NAME: str = "SD Media / Седа У."
    PAYEE_BANK: str = "Т-Банк"
    PAYEE_ACCOUNT: str = "5536 **** **** 1234"  # замени на реальные

    # === Файловое хранилище ===
    TIMEZONE: str = "Europe/Moscow"
    DATA_FILE: str = "data/users.json"

    # === Превью «Архив знаний» (обложки гайдов) ===
    # Можно URL или Telegram file_id (если уже грузила обложки боту и сохранила ID).
    ARCHIVE_PHOTOS: List[str] = [
        "https://your.cdn/guide_cover_01.jpg",
        "https://your.cdn/guide_cover_02.jpg",
        "https://your.cdn/guide_cover_03.jpg",
    ]
    ARCHIVE_CAPTION: str = "Гайды, чек-листы и шпаргалки. Обновляем регулярно."

settings = Settings()
