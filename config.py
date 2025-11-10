from dataclasses import dataclass
from typing import Tuple

@dataclass
class Settings:
    # Токен бота из BotFather
    BOT_TOKEN: str = "ВАШ_TELEGRAM_BOT_TOKEN"

    # ID админов, которые могут вызывать /set_sub /stats и т.п.
    ADMINS: Tuple[int, ...] = (123456789,)

    # Куда слать запросы "связаться с куратором" и ответы на чек-ин
    ADMIN_CHAT_ID: int = 123456789

    # Ссылки — потом подставишь свои
    SUBSCRIPTION_LINK: str = "https://example.com/pay"
    MATERIALS_LINK: str = "https://t.me/your_materials_channel"
    SEASONS_LINK: str = "https://example.com/seasons"

    # Файл для хранения данных (Render сам создаст папку)
    TIMEZONE: str = "Europe/Moscow"
    DATA_FILE: str = "data/users.json"

settings = Settings()
