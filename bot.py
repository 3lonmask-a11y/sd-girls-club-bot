import asyncio
import json
from datetime import date
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
    """
    Главное меню по твоему плану:
    Канал / Чат / Архив знаний / Моя подписка / Подарить подписку / Сезоны клуба / Связаться с куратором
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Канал", callback_data="channel")],
            [InlineKeyboardButton(text="Чат", callback_data="chat")],
            [InlineKeyboardButton(text="Архив знаний", callback_data="archive")],
            [InlineKeyboardButton(text="Моя подписка", callback_data="access")],
            [InlineKeyboardButton(text="Подарить подписку", callback_data="gift")],
            [InlineKeyboardButton(text="Сезоны клуба", callback_data="seasons")],
            [InlineKeyboardButton(text="Связаться с куратором", callback_data="support")],
        ]
    )


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu")]
        ]
    )


# ---------- КОМАНДЫ ----------

async def cmd_start(message: Message):
    full_name = message.from_user.full_name if message.from_user else ""
    text = (
        f"Привет, {full_name}.\n"
        "Я система SD GIRLS CLUB.\n"
        "Держу тебя в курсе сезонов, материалов и доступа.\n"
        "Без шума, без спама. Всё по делу.\n\n"
        "Выбери, что тебе нужно сейчас:"
    )
    await message.answer(text, reply_markup=main_menu_kb())


async def cmd_menu(message: Message):
    await message.answer(
        "Меню SD GIRLS CLUB.\n"
        "Отсюда — ко всем рабочим разделам.",
        reply_markup=main_menu_kb()
    )


async def cmd_set_sub(message: Message, command: CommandObject):
    # /set_sub YYYY-MM-DD (только админ)
    if not is_admin(message.from_user.id):
        return

    if not command.args:
        await message.answer(
            "Формат: /set_sub YYYY-MM-DD (ответом на сообщение пользователя или для себя)."
        )
        return

    try:
        end = date.fromisoformat(command.args.strip())
    except ValueError:
        await message.answer("Неверный формат. Используй YYYY-MM-DD.")
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    else:
        target = message.from_user.id

    set_user(target, {"subscription_end": end.isoformat()})
    await message.answer(f"Подписка для {target} до {end.isoformat()}")


async def cmd_stats(message: Message):
    # Статистика по пользователям (только админ)
    if not is_admin(message.from_user.id):
        return

    data = load_data()
    total = len(data)
    active = sum(1 for u in data.values() if is_active(u))

    await message.answer(f"Всего пользователей: {total}\nАктивных подписок: {active}")


# ---------- CALLBACK ХЕНДЛЕРЫ МЕНЮ ----------

async def cb_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Меню SD GIRLS CLUB.\nОтсюда — ко всем рабочим разделам.",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


async def cb_channel(callback: CallbackQuery):
    text = (
        "Официальный канал SD GIRLS CLUB.\n"
        "Анонсы, ориентиры, важные сигналы.\n\n"
        f"{settings.CLUB_CHANNEL_LINK}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_chat(callback: CallbackQuery):
    text = (
        "Чат участниц SD GIRLS CLUB.\n"
        "Тихое сообщество без базара и агрессии.\n\n"
        f"{settings.CLUB_CHAT_LINK}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_archive(callback: CallbackQuery):
    text = (
        "Архив знаний SD GIRLS CLUB.\n"
        "Гайды, чек-листы и шпаргалки, к которым можно возвращаться.\n\n"
        f"{settings.MATERIALS_LINK}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_seasons(callback: CallbackQuery):
    text = (
        "Сезоны клуба и ближайшие форматы.\n\n"
        "1. Сезоны — длительные программы с мягкими ежедневными шага́ми.\n"
        "2. Челленджи — точечная работа: деньги, дом, тело, стиль.\n"
        "3. Интенсивы — для тех, кто хочет глубже.\n\n"
        f"Описание и регистрация: {settings.SEASONS_LINK}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_access(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    end = user.get("subscription_end")

    if is_active(user):
        text = (
            f"Твой доступ к SD GIRLS CLUB активен до {end}.\n"
            "Можно спокойно продолжать в своём ритме."
        )
    elif end:
        text = (
            f"Твой доступ был до {end}, сейчас он завершён.\n\n"
            "Если формат тебе подходит — можно вернуться в любой момент:\n"
            f"{settings.SUBSCRIPTION_LINK}"
        )
    else:
        text = (
            "Сейчас у тебя нет активного доступа.\n\n"
            "Если ты уже оплачивала — напиши куратору через меню.\n"
            "Если хочешь присоединиться:\n"
            f"{settings.SUBSCRIPTION_LINK}"
        )

    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_gift(callback: CallbackQuery):
    text = (
        "Подарить доступ в SD GIRLS CLUB.\n"
        "Адекватный подарок: ритм, опора и порядок вместо мусора.\n\n"
        f"Оформить подарок: {getattr(settings, 'GIFT_SUBSCRIPTION_LINK', settings.SUBSCRIPTION_LINK)}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_support(callback: CallbackQuery):
    # включаем режим "жду сообщение для куратора"
    set_user(callback.from_user.id, {"wait_support": True})
    text = (
        "Опиши одним сообщением, в чём вопрос: доступ, оплата, материалы или другое.\n"
        "Я передам это куратору, ответ придёт сюда."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ---------- СООБЩЕНИЯ КУРАТОРУ ----------

async def support_router(message: Message, bot: Bot):
    # ловим текст, если до этого нажали "Связаться с куратором"
    if not message.text or message.text.startswith("/"):
        return

    user = get_user(message.from_user.id)
    if not user.get("wait_support"):
        return

    set_user(message.from_user.id, {"wait_support": False})

    text = (
        f"Запрос в поддержку от @{message.from_user.username or message.from_user.id} "
        f"(id={message.from_user.id}):\n"
        f"{message.text}"
    )
    await bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=text)
    await message.answer("Сообщение передано куратору. Ответ придёт сюда.")


# ---------- MAIN ----------

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_set_sub, Command("set_sub"))
    dp.message.register(cmd_stats, Command("stats"))

    # callback-кнопки меню
    dp.callback_query.register(cb_menu, F.data == "menu")
    dp.callback_query.register(cb_channel, F.data == "channel")
    dp.callback_query.register(cb_chat, F.data == "chat")
    dp.callback_query.register(cb_archive, F.data == "archive")
    dp.callback_query.register(cb_seasons, F.data == "seasons")
    dp.callback_query.register(cb_access, F.data == "access")
    dp.callback_query.register(cb_gift, F.data == "gift")
    dp.callback_query.register(cb_support, F.data == "support")

    # сообщения в поддержку
    dp.message.register(support_router, F.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
