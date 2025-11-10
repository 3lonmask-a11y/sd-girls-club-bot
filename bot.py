import asyncio
import json
from datetime import date, datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.client.default import DefaultBotProperties

from config import settings

# ---------- ВРЕМЯ ОТКРЫТИЯ КЛУБА ----------

RELEASE_DATE = (2025, 11, 11, 11, 11)

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo(getattr(settings, "TIMEZONE", "Europe/Moscow"))
except Exception:
    TZ = None


def now():
    if TZ:
        return datetime.now(TZ)
    return datetime.utcnow()


def is_open() -> bool:
    year, month, day, hour, minute = RELEASE_DATE
    if TZ:
        release_at = datetime(year, month, day, hour, minute, tzinfo=TZ)
    else:
        release_at = datetime(year, month, day, hour, minute)
    return now() >= release_at


# ---------- ХРАНИЛИЩЕ ДАННЫХ ----------

DATA_PATH = Path(settings.DATA_FILE)
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_data() -> dict:
    if not DATA_PATH.exists():
        return {}
    with DATA_PATH.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(uid: int) -> dict:
    data = load_data()
    return data.get(str(uid), {})


def set_user(uid: int, info: dict) -> None:
    data = load_data()
    current = data.get(str(uid), {})
    current.update(info)
    data[str(uid)] = current
    save_data(data)


def is_admin(uid: int) -> bool:
    return uid in settings.ADMINS


def is_active(user: dict) -> bool:
    end = user.get("subscription_end")
    if not end:
        return False
    try:
        d = date.fromisoformat(end)
    except ValueError:
        return False
    return d >= date.today()


# ---------- КЛАВИАТУРЫ ----------

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Канал", callback_data="channel")],
            [
                InlineKeyboardButton(
                    text="💬 Чат клуба",
                    url=getattr(settings, "CLUB_CHAT_LINK", "https://t.me/+rH3eJ6oMO-ljYmYy"),
                )
            ],
            [InlineKeyboardButton(text="Архив знаний", callback_data="archive")],
            [InlineKeyboardButton(text="Моя подписка", callback_data="access")],
            [InlineKeyboardButton(text="Подарить подписку", callback_data="gift")],
            [InlineKeyboardButton(text="Сезоны клуба", callback_data="seasons")],
            [InlineKeyboardButton(text="Связаться с куратором", callback_data="support")],
        ]
    )


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад в меню", callback_data="menu")]]
    )


# ---------- ТЕКСТЫ ----------

def prelaunch_text(full_name: str | None = None) -> str:
    name = f"{full_name}, " if full_name else ""
    return (
        f"{name}SD GIRLS CLUB готов.\n"
        "Официальное открытие — 11.11 в 11:11.\n\n"
        "Это закрытое пространство для спокойного, собранного ритма.\n"
        "Если ты здесь раньше — просто останься. Я напомню и открою доступ в нужный момент."
    )


def locked_section_text() -> str:
    return "Полный доступ к разделам клуба откроется 11.11 в 11:11."


def text_channel() -> str:
    return (
        "Официальный канал SD GIRLS CLUB.\n"
        "Анонсы, ориентиры, важные сигналы.\n\n"
        "👉 https://t.me/+vv7kwR01r2I4NjQy"
    )


def text_archive() -> str:
    return (
        "Архив знаний SD GIRLS CLUB.\n"
        "Гайды, чек-листы и шпаргалки, к которым можно возвращаться.\n\n"
        f"{settings.MATERIALS_LINK}"
    )


def text_seasons() -> str:
    return (
        "Сезоны клуба и ближайшие форматы.\n\n"
        "1. Сезоны — длительные программы с мягкими ежедневными шагами.\n"
        "2. Челленджи — точечная работа: деньги, дом, тело, стиль.\n"
        "3. Интенсивы — для тех, кто хочет глубже.\n\n"
        f"Описание и регистрация: {settings.SEASONS_LINK}"
    )


def text_gift() -> str:
    link = getattr(settings, "GIFT_SUBSCRIPTION_LINK", settings.SUBSCRIPTION_LINK)
    return (
        "Подарить доступ в SD GIRLS CLUB.\n"
        "Адекватный подарок: ритм, опора и порядок вместо мусора.\n\n"
        f"Оформить подарок: {link}"
    )


# ---------- КОМАНДЫ ----------

async def cmd_start(message: Message):
    full_name = message.from_user.full_name if message.from_user else ""
    if not is_open():
        await message.answer(prelaunch_text(full_name))
        return

    text = (
        f"Привет, {full_name}.\n"
        "Я система SD GIRLS CLUB.\n"
        "Помогаю держать в порядке доступ, сезоны и материалы.\n"
        "Без шума, без спама. Всё по делу.\n\n"
        "Выбери, что тебе нужно сейчас:"
    )
    await message.answer(text, reply_markup=main_menu_kb())


async def cmd_menu(message: Message):
    if not is_open():
        await message.answer(prelaunch_text(message.from_user.full_name if message.from_user else ""))
        return
    await message.answer("Меню SD GIRLS CLUB.\nОтсюда — ко всем рабочим разделам.", reply_markup=main_menu_kb())


async def cmd_support(message: Message):
    set_user(message.from_user.id, {"wait_support": True})
    await message.answer(
        "Опиши одним сообщением, в чём вопрос: доступ, оплата, материалы или другое.\n"
        "Я передам это куратору, ответ придёт сюда.",
        reply_markup=back_kb(),
    )


# ---------- CALLBACK ХЕНДЛЕРЫ ----------

async def cb_channel(callback: CallbackQuery):
    if not is_open():
        await callback.answer("Канал станет доступен после открытия 11.11 в 11:11.", show_alert=True)
        return
    await callback.message.edit_text(text_channel(), reply_markup=back_kb())
    await callback.answer()


# остальное оставляем как было


# ---------- MAIN ----------

async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_support, Command("support"))

    dp.callback_query.register(cb_channel, F.data == "channel")

    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
