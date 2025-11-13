# config.py
from dataclasses import dataclass, field
from typing import Tuple, List
import os


def env_str(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return val if val is not None else default


def env_int(name: str, default: int) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


@dataclass
class Settings:
    # 🔐 Токен бота (из переменных окружения Render)
    BOT_TOKEN: str = env_str("BOT_TOKEN", "")

    # 👑 Админы (ID через BotFather /getid, сюда — числа)
    ADMINS: Tuple[int, ...] = (931831277,)
    ADMIN_CHAT_ID: int = env_int("ADMIN_CHAT_ID", 931831277)

    # 🔗 Ссылки (можешь потом задать в Environment, а можешь оставить хардкод)
    CLUB_CHANNEL_LINK: str = env_str("CLUB_CHANNEL_LINK", "https://t.me/your_channel")
    CLUB_CHAT_LINK: str = env_str("CLUB_CHAT_LINK", "https://t.me/your_chat")
    MATERIALS_LINK: str = env_str("MATERIALS_LINK", "https://t.me/your_materials")
    SEASONS_LINK: str = env_str("SEASONS_LINK", "https://example.com/seasons")
    SUBSCRIPTION_LINK: str = env_str("SUBSCRIPTION_LINK", "https://example.com/pay")

    # 🎁 (если пока не нужно — можно не задавать)
    GIFT_SUBSCRIPTION_LINK: str = env_str("GIFT_SUBSCRIPTION_LINK", "")

    # 💳 Реквизиты для ручной оплаты
    PAYEE_NAME: str = env_str("PAYEE_NAME", "ФИО получателя")
    PAYEE_BANK: str = env_str("PAYEE_BANK", "Т-Банк")
    PAYEE_ACCOUNT: str = env_str("PAYEE_ACCOUNT", "XXXX XXXX XXXX XXXX")
    SUBSCRIPTION_PRICE: int = env_int("SUBSCRIPTION_PRICE", 590)

    # ⏳ Сколько дней длится подписка
    SUBSCRIPTION_DAYS: int = env_int("SUBSCRIPTION_DAYS", 30)

    # 📁 Файл, где бот хранит данные пользователей
    DATA_FILE: str = env_str("DATA_FILE", "data/users.json")

    # 🖼 Фотки для блока «Архив знаний» (file_id или URL)
    # можно оставить пустым, можно добавить свои file_id
    ARCHIVE_PHOTOS: List[str] = field(default_factory=list)


settings = Settings()
