from dataclasses import dataclass
import os
from typing import Tuple


@dataclass
class Settings:
    # Токен бота — теперь читается из Render Environment (BOT_TOKEN)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")

    # Реквизиты для оплаты
    PAYMENT_DETAILS: str = """Получатель: ...
Банк: ...
Карта / счет: ...
Сумма: 590 ₽
Комментарий: SD GIRLS CLUB + твой ник в Telegram"""

    # ID админов
    ADMINS: Tuple[int, ...] = (931831277,)

    # ID чата куратора
    ADMIN_CHAT_ID: int = 931831277

    # Ссылки — подставь свои
    SUBSCRIPTION_LINK: str = "https://b2b.cbrpay.ru/BS1B0015GJF90OHV8P4B4JO82PGHN395"
    MATERIALS_LINK: str = "https://t.me/your_materials_channel"
    SEASONS_LINK: str = "https://example.com/seasons"

    # Настройки
    TIMEZONE: str = "Europe/Moscow"
    DATA_FILE: str = "data/users.json"


settings = Settings()
