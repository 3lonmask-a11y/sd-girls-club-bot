from dataclasses import dataclass
from typing import Tuple

@dataclass
class Settings:
    # Токен бота из BotFather
    BOT_TOKEN: str = "8344740572:AAFgGaZl0Bu-CFc05V3TKFYNIdEeKpAEs94"

    # ID админов, которые могут вызывать /set_sub /stats и т.п.
    ADMINS: Tuple[int, ...] = (931831277,)

    # Куда слать запросы "связаться с куратором" и ответы на чек-ин
    ADMIN_CHAT_ID: int = 931831277

    # Ссылки — потом подставишь свои
    SUBSCRIPTION_LINK: str = "https://b2b.cbrpay.ru/BS1B0015GJF90OHV8P4B4JO82PGHN395"
    MATERIALS_LINK: str = "https://t.me/your_materials_channel"
    SEASONS_LINK: str = "https://example.com/seasons"

    # Файл для хранения данных (Render сам создаст папку)
    TIMEZONE: str = "Europe/Moscow"
    DATA_FILE: str = "data/users.json"

settings = Settings()

