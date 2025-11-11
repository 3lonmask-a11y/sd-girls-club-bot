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
    Главное меню:
    Канал / Чат / Архив / Моя подписка / Оплатить / Подарить / Сезоны / Поддержка
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Канал", callback_data="channel")],
            [InlineKeyboardButton(
                text="Чат клуба",
                url=getattr(settings, "CLUB_CHAT_LINK", "https://t.me/")  # подставь свой
            )],
            [InlineKeyboardButton(text="Архив знаний", callback_data="archive")],
            [InlineKeyboardButton(text="Моя подписка", callback_data="access")],
            [InlineKeyboardButton(text="Оплатить подписку", callback_data="pay")],
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


# ---------- ТЕКСТОВЫЕ БЛОКИ ----------

def text_channel() -> str:
    return (
        "Официальный канал SD GIRLS CLUB.\n"
        "Анонсы, ориентиры, важные сигналы.\n\n"
        f"{settings.CLUB_CHANNEL_LINK}"
    )


def text_archive() -> str:
    return (
        "Архив знаний SD GIRLS CLUB.\n"
        "Гайды, чек-листы и материалы, к которым можно возвращаться.\n\n"
        f"{settings.MATERIALS_LINK}"
    )


def text_seasons() -> str:
    return (
        "Сезоны клуба и ближайшие форматы.\n\n"
        "1. Сезоны — мягкие долгие программы.\n"
        "2. Челленджи — точечная работа: деньги, дом, тело, стиль.\n"
        "3. Интенсивы — для тех, кто хочет глубже.\n\n"
        f"Описание и регистрация: {settings.SEASONS_LINK}"
    )


def text_gift() -> str:
    link = getattr(settings, "GIFT_SUBSCRIPTION_LINK", "")
    core = (
        "Подарить доступ в SD GIRLS CLUB.\n"
        "Подарок, который усиливает, а не захламляет.\n\n"
    )
    if link:
        core += f"Оформить подарок: {link}"
    else:
        core += "Напиши куратору, если хочешь оформить подарок."
    return core


# ---------- ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ ----------

async def cmd_start(message: Message):
    full_name = message.from_user.full_name if message.from_user else ""
    text = (
        f"Привет, {full_name}.\n"
        "Я система SD GIRLS CLUB.\n"
        "Помогаю с доступом, навигацией и связью с куратором.\n"
        "Без шума, без спама. Всё по делу.\n\n"
        "Выбери, что тебе нужно:"
    )
    await message.answer(text, reply_markup=main_menu_kb())


async def cmd_menu(message: Message):
    await message.answer(
        "Меню SD GIRLS CLUB.\n"
        "Отсюда — ко всем рабочим разделам.",
        reply_markup=main_menu_kb(),
    )


async def cmd_access(message: Message):
    user = get_user(message.from_user.id)
    end = user.get("subscription_end")

    if is_active(user):
        text = (
            f"Твой доступ к SD GIRLS CLUB активен до {end}.\n"
            "Можно спокойно продолжать в своём ритме."
        )
    elif end:
        text = (
            f"Твой доступ был до {end}, сейчас он завершён.\n\n"
            "Если формат подходит — можно вернуться в любой момент.\n"
            "Напиши куратору или посмотри, как оплатить в меню."
        )
    else:
        text = (
            "Сейчас у тебя нет активного доступа.\n\n"
            "Нажми «Оплатить подписку» в меню, чтобы получить реквизиты.\n"
            "После оплаты пришли скрин — куратор подтвердит участие."
        )
    await message.answer(text, reply_markup=back_kb())


async def cmd_support(message: Message):
    set_user(message.from_user.id, {"wait_support": True})
    text = (
        "Опиши одним сообщением, в чём вопрос: доступ, оплата, материалы или другое.\n"
        "Я передам это куратору, ответ придёт сюда."
    )
    await message.answer(text, reply_markup=back_kb())


# ---------- АДМИН-КОМАНДЫ ----------

async def cmd_set_sub(message: Message, command: CommandObject):
    # /set_sub YYYY-MM-DD (только админ)
    if not is_admin(message.from_user.id):
        return

    if not command.args:
        await message.answer(
            "Формат: /set_sub YYYY-MM-DD (ответом на сообщение пользователя или с указанием для себя)."
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
    if not is_admin(message.from_user.id):
        return

    data = load_data()
    total = len(data)
    active = sum(1 for u in data.values() if is_active(u))
    await message.answer(f"Всего пользователей: {total}\nАктивных подписок: {active}")


# ---------- CALLBACK ХЕНДЛЕРЫ ----------

async def cb_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Меню SD GIRLS CLUB.\nОтсюда — ко всем рабочим разделам.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


async def cb_channel(callback: CallbackQuery):
    await callback.message.edit_text(text_channel(), reply_markup=back_kb())
    await callback.answer()


async def cb_archive(callback: CallbackQuery):
    await callback.message.edit_text(text_archive(), reply_markup=back_kb())
    await callback.answer()


async def cb_seasons(callback: CallbackQuery):
    await callback.message.edit_text(text_seasons(), reply_markup=back_kb())
    await callback.answer()


async def cb_access(callback: CallbackQuery):
    # та же логика, что и cmd_access
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
            "Если формат подходит — можно вернуться в любой момент.\n"
            "Напиши куратору или посмотри, как оплатить в меню."
        )
    else:
        text = (
            "Сейчас у тебя нет активного доступа.\n\n"
            "Нажми «Оплатить подписку», чтобы получить реквизиты.\n"
            "После оплаты пришли скрин — куратор подтвердит участие."
        )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_pay(callback: CallbackQuery):
    # включаем режим ожидания скрина
    set_user(callback.from_user.id, {"waiting_payment": True})
    text = (
        "Реквизиты для оплаты участия в SD GIRLS CLUB:\n\n"
        f"{settings.PAYMENT_DETAILS}\n\n"
        "После оплаты:\n"
        "1. Сделай скриншот или фото подтверждения.\n"
        "2. Отправь его сюда одним сообщением.\n\n"
        "Я передам данные куратору, он подтвердит доступ."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_gift(callback: CallbackQuery):
    await callback.message.edit_text(text_gift(), reply_markup=back_kb())
    await callback.answer()


async def cb_support(callback: CallbackQuery):
    set_user(callback.from_user.id, {"wait_support": True})
    text = (
        "Опиши одним сообщением, в чём вопрос: доступ, оплата, материалы или другое.\n"
        "Я передам это куратору, ответ придёт сюда."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ---------- ОБРАБОТКА СКРИНОВ ОПЛАТЫ И СООБЩЕНИЙ КУРАТОРУ ----------

async def payment_proof_router(message: Message, bot: Bot):
    """
    Ловим скрин/фото/документ, если пользователь в режиме waiting_payment.
    """
    user = get_user(message.from_user.id)
    if not user.get("waiting_payment"):
        return

    # сбрасываем флаг
    set_user(message.from_user.id, {"waiting_payment": False})

    # пробрасываем админам доказательство
    caption = (
        f"🔔 Возможная оплата подписки.\n"
        f"Пользователь: @{message.from_user.username or 'без_username'} (id={message.from_user.id}).\n"
        "Проверь по реквизитам и активируй доступ через /set_sub."
    )

    # если есть фото
    if message.photo:
        file_id = message.photo[-1].file_id
        await bot.send_photo(
            chat_id=settings.ADMIN_CHAT_ID,
            photo=file_id,
            caption=caption,
        )
    # если документ (PDF/скрин)
    elif message.document:
        await bot.send_document(
            chat_id=settings.ADMIN_CHAT_ID,
            document=message.document.file_id,
            caption=caption,
        )
    else:
        # если почему-то без вложения
        await bot.send_message(
            chat_id=settings.ADMIN_CHAT_ID,
            text=caption + "\n(без вложения, пользователь что-то сделал не так)",
        )

    await message.answer(
        "Я передала чек куратору.\n"
        "После проверки доступ будет активирован, сообщение придёт сюда."
    )


async def support_router(message: Message, bot: Bot):
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

    # публичные команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_access, Command("access"))
    dp.message.register(cmd_support, Command("support"))

    # админ-команды
    dp.message.register(cmd_set_sub, Command("set_sub"))
    dp.message.register(cmd_stats, Command("stats"))

    # callbacks
    dp.callback_query.register(cb_menu, F.data == "menu")
    dp.callback_query.register(cb_channel, F.data == "channel")
    dp.callback_query.register(cb_archive, F.data == "archive")
    dp.callback_query.register(cb_seasons, F.data == "seasons")
    dp.callback_query.register(cb_access, F.data == "access")
    dp.callback_query.register(cb_pay, F.data == "pay")
    dp.callback_query.register(cb_gift, F.data == "gift")
    dp.callback_query.register(cb_support, F.data == "support")

    # скрины оплаты
    dp.message.register(payment_proof_router, F.photo | F.document)

    # сообщения в поддержку
    dp.message.register(support_router, F.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
