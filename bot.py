# bot.py
import asyncio
import json
from datetime import date, timedelta
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)

from config import settings

# ========= НАСТРОЙКИ / ФАЙЛ ХРАНИЛИЩА =========
DATA_PATH = Path(settings.DATA_FILE)
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

SUB_DAYS = settings.SUBSCRIPTION_DAYS or 30  # страховка


# ========= ХРАНИЛИЩЕ ДАННЫХ =========
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


def was_approved(uid: int) -> bool:
    return bool(get_user(uid).get("subscription_end"))


# ========= КЛАВИАТУРЫ =========
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Канал", callback_data="channel")],
            [InlineKeyboardButton(text="💬 Чат клуба", callback_data="chat")],
            [InlineKeyboardButton(text="📚 Архив знаний", callback_data="archive")],
            [InlineKeyboardButton(text="🪪 Моя подписка", callback_data="access")],
            [InlineKeyboardButton(text="💠 Оплатить / продлить", callback_data="pay")],
            [InlineKeyboardButton(text="🎁 Подарить доступ", callback_data="gift")],
            [InlineKeyboardButton(text="🗓️ Сезоны клуба", callback_data="seasons")],
            [InlineKeyboardButton(text="🤍 Связаться с куратором", callback_data="support")],
        ]
    )


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="‹ Назад в меню", callback_data="menu")]]
    )


# ========= КОМАНДЫ =========
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
        "Меню SD GIRLS CLUB.\nОтсюда — ко всем рабочим разделам.",
        reply_markup=main_menu_kb(),
    )


async def cmd_set_sub(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("Формат: /set_sub YYYY-MM-DD (ответом на пользователя или для себя).")
    try:
        end = date.fromisoformat(command.args.strip())
    except ValueError:
        return await message.answer("Неверный формат. Используй YYYY-MM-DD.")
    target = message.reply_to_message.from_user.id if message.reply_to_message and message.reply_to_message.from_user else message.from_user.id
    set_user(target, {"subscription_end": end.isoformat()})
    await message.answer(f"Подписка для {target} до {end.isoformat()}")


async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    data = load_data()
    total = len(data)
    active = sum(1 for u in data.values() if is_active(u))
    await message.answer(f"Всего пользователей: {total}\nАктивных подписок: {active}")


# ========= ХЕЛПЕРЫ =========
async def send_album_with_link(chat_id: int, bot: Bot):
    photos = getattr(settings, "ARCHIVE_PHOTOS", [])
    if photos:
        media = []
        for i, src in enumerate(photos):
            if i == 0:
                media.append(InputMediaPhoto(media=src, caption=settings.ARCHIVE_CAPTION))
            else:
                media.append(InputMediaPhoto(media=src))
        await bot.send_media_group(chat_id=chat_id, media=media)

    open_btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Открыть архив", url=settings.MATERIALS_LINK)],
            [InlineKeyboardButton(text="‹ Назад в меню", callback_data="menu")],
        ]
    )
    await bot.send_message(chat_id, "Собрали всё спокойное и полезное в одном месте.", reply_markup=open_btn)


# ========= CALLBACK: МЕНЮ =========
async def cb_menu(callback: CallbackQuery):
    await callback.message.edit_text("Меню SD GIRLS CLUB.\nОтсюда — ко всем рабочим разделам.", reply_markup=main_menu_kb())
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
        "Тихое сообщество без шума и агрессии.\n\n"
        f"{settings.CLUB_CHAT_LINK}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_archive(callback: CallbackQuery):
    await callback.answer()
    # Можно не удалять предыдущий экран — тогда убери строку ниже
    await callback.message.delete()
    await send_album_with_link(chat_id=callback.from_user.id, bot=callback.bot)


async def cb_seasons(callback: CallbackQuery):
    text = (
        "Сезоны и форматы SD GIRLS CLUB:\n\n"
        "1. Сезоны — мягкие длительные маршруты.\n"
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
        text = f"Твой доступ к SD GIRLS CLUB активен до {end}.\nМожно спокойно продолжать в своём ритме."
    elif end:
        text = (
            f"Твой доступ был до {end}, сейчас он завершён.\n\n"
            "Чтобы вернуться:\n• Нажми «💠 Оплатить / продлить».\n• Оплати по реквизитам и пришли чек сюда."
        )
    else:
        text = (
            "Сейчас у тебя нет активного доступа.\n\n"
            "Если уже оплачивала — нажми «🤍 Связаться с куратором» и приложи чек.\n"
            "Если хочешь присоединиться:\n• Нажми «💠 Оплатить / продлить» и следуй инструкции."
        )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


async def cb_gift(callback: CallbackQuery):
    # Подарочная механика остаётся ручной (перевод + чек)
    text = (
        "Подарить доступ в SD GIRLS CLUB.\n"
        "Аккуратный подарок: ритм, опора и порядок.\n\n"
        "Как оформить:\n• Оплати по тем же реквизитам, в комментарии укажи ник дарящей и получательницы.\n"
        "• Пришли чек сюда — мы активируем доступ."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ========= ОПЛАТА: РУЧНЫЕ РЕКВИЗИТЫ + ЧЕК =========
async def cb_pay(callback: CallbackQuery):
    uid = callback.from_user.id
    pay_text = (
        "<b>Реквизиты для оплаты участия в SD GIRLS CLUB</b>\n\n"
        f"<b>Получатель:</b> {settings.PAYEE_NAME}\n"
        f"<b>Банк:</b> {settings.PAYEE_BANK}\n"
        f"<b>Карта / счёт:</b> <code>{settings.PAYEE_ACCOUNT}</code>\n"
        f"<b>Сумма:</b> {settings.SUBSCRIPTION_PRICE} ₽\n"
        f"<b>Комментарий:</b> <code>SD GIRLS CLUB + твой ник в Telegram</code>\n\n"
        "После оплаты:\n"
        "1) сделай скрин/фото подтверждения;\n"
        "2) отправь сюда <b>одним сообщением</b>.\n\n"
        f"После проверки бот включит доступ на <b>{SUB_DAYS} дней</b> и сообщит здесь."
    )
    set_user(uid, {"wait_payment": True})
    await callback.message.edit_text(pay_text, reply_markup=back_kb())
    await callback.answer()


# ========= СВЯЗЬ С КУРАТОРОМ =========
async def cb_support(callback: CallbackQuery):
    uid = callback.from_user.id
    set_user(uid, {"wait_support": True})
    text = (
        "Опиши одним сообщением, в чём вопрос: доступ, оплата, материалы или другое.\n"
        "Я передам это куратору, ответ придёт сюда."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ========= ОБРАБОТКА СООБЩЕНИЙ =========
async def payment_router(message: Message, bot: Bot):
    user = get_user(message.from_user.id)
    if not user.get("wait_payment"):
        return
    if not (message.photo or message.document or message.text):
        return

    set_user(message.from_user.id, {"wait_payment": False})
    uid = message.from_user.id
    username = message.from_user.username or "без_username"

    admin_text = (
        "🔔 Возможная оплата подписки.\n"
        f"Пользователь: @{username} (id={uid}).\n\n"
        "Проверь по реквизитам. Если всё ok — нажми ✅, бот включит доступ и сообщит участнице."
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"approve:{uid}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{uid}"),
            ]
        ]
    )

    if message.photo or message.document:
        await message.copy_to(chat_id=settings.ADMIN_CHAT_ID, caption=admin_text, reply_markup=kb)
    else:
        await bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=f"{admin_text}\n\nСообщение:\n{message.text}", reply_markup=kb)

    await message.answer("Я передала чек куратору. После проверки доступ будет активирован, сообщение придёт сюда.")


async def support_router(message: Message, bot: Bot):
    if not message.text:
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


# ========= CALLBACK: АДМИН ПОДТВЕРЖДАЕТ / ОТКЛОНЯЕТ =========
async def cb_approve(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Недостаточно прав", show_alert=True)
    try:
        uid = int(callback.data.split(":", 1)[1])
    except (IndexError, ValueError):
        return await callback.answer("Ошибка данных", show_alert=True)
    if was_approved(uid):
        return await callback.answer("Уже активировано ранее", show_alert=True)

    end = date.today() + timedelta(days=SUB_DAYS)
    set_user(uid, {"subscription_end": end.isoformat()})
    await callback.answer("Доступ выдан.")
    try:
        await bot.send_message(uid, f"Твой доступ к SD GIRLS CLUB активирован до {end}. Добро пожаловать 💗")
    except Exception:
        pass


async def cb_reject(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Недостаточно прав", show_alert=True)
    try:
        uid = int(callback.data.split(":", 1)[1])
    except (IndexError, ValueError):
        return await callback.answer("Ошибка данных", show_alert=True)

    await callback.answer("Отмечено как не подтверждено.")
    try:
        await bot.send_message(uid, "Платёж не удалось подтвердить. Проверь сумму/реквизиты или напиши куратору — разберёмся аккуратно.")
    except Exception:
        pass


# ========= MAIN =========
async def main():
    # Токен: сначала пытаемся взять из ENV, иначе из config
    import os
    token = os.getenv("BOT_TOKEN") or settings.BOT_TOKEN
    if not token:
        raise RuntimeError("BOT_TOKEN не задан. Укажи в Render > Environment или в config.py.")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_set_sub, Command("set_sub"))
    dp.message.register(cmd_stats, Command("stats"))

    # callbacks: меню
    dp.callback_query.register(cb_menu, F.data == "menu")
    dp.callback_query.register(cb_channel, F.data == "channel")
    dp.callback_query.register(cb_chat, F.data == "chat")
    dp.callback_query.register(cb_archive, F.data == "archive")
    dp.callback_query.register(cb_seasons, F.data == "seasons")
    dp.callback_query.register(cb_access, F.data == "access")
    dp.callback_query.register(cb_pay, F.data == "pay")
    dp.callback_query.register(cb_gift, F.data == "gift")
    dp.callback_query.register(cb_support, F.data == "support")

    # callbacks: подтверждение / отказ оплаты
    dp.callback_query.register(cb_approve, F.data.startswith("approve:"))
    dp.callback_query.register(cb_reject, F.data.startswith("reject:"))

    # сообщения: сначала оплата, потом поддержка (по статусам)
    dp.message.register(payment_router)
    dp.message.register(support_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

