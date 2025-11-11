from dataclasses import dataclass
import os
from typing import Tuple


@dataclass
class Settings:
    # Токен бота — только из переменных окружения Render
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # Админы
    # Можно задать ADMIN_ID и ADMIN_CHAT_ID в Environment,
    # иначе по умолчанию твой id (поставь свой реальный).
    MAIN_ADMIN_ID: int = int(os.getenv("ADMIN_ID", "931831277"))
    ADMINS: Tuple[int, ...] = (
        MAIN_ADMIN_ID,
    )
    ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", str(MAIN_ADMIN_ID)))

    # Ссылки (подставь свои через Environment или оставь заглушки)
    SUBSCRIPTION_LINK: str = os.getenv(
        "SUBSCRIPTION_LINK",
        "https://b2b.cbrpay.ru/BS1B0015GJF90OHV8P4B4JO82PGHN395",
    )
    MATERIALS_LINK: str = os.getenv(
        "MATERIALS_LINK",
        "https://t.me/your_materials_channel",
    )
    SEASONS_LINK: str = os.getenv(
        "SEASONS_LINK",
        "https://example.com/seasons",
    )

    # Линки на канал и чат клуба
    CLUB_CHANNEL_LINK: str = os.getenv(
        "CLUB_CHANNEL_LINK",
        "https://t.me/your_club_channel",
    )
    CLUB_CHAT_LINK: str = os.getenv(
        "CLUB_CHAT_LINK",
        "https://t.me/your_club_chat",
    )

    # Параметры оплаты (вызываются в cb_pay)
    PAYEE_NAME: str = os.getenv("PAYEE_NAME", "Получатель")
    PAYEE_BANK: str = os.getenv("PAYEE_BANK", "Банк")
    PAYEE_ACCOUNT: str = os.getenv("PAYEE_ACCOUNT", "XXXX XXXX XXXX XXXX")
    SUBSCRIPTION_PRICE: int = int(os.getenv("SUBSCRIPTION_PRICE", "590"))

    # Длительность подписки по умолчанию (дней)
    SUBSCRIPTION_DAYS: int = int(os.getenv("SUBSCRIPTION_DAYS", "30"))

    # Техническое
    TIMEZONE: str = os.getenv("TZ", "Europe/Moscow")
    DATA_FILE: str = os.getenv("DATA_FILE", "data/users.json")


settings = Settings()
