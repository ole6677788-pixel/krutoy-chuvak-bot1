import os
from html import escape

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6542085968
CHANNEL_ID = -1003076484178


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Предложить шнягу", callback_data="suggest")],
        [InlineKeyboardButton("🥤 Оценить газяву", callback_data="soda_rate")],
        [
            InlineKeyboardButton("📜 Правила", callback_data="rules"),
            InlineKeyboardButton("ℹ️ О боте", callback_data="about"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("mode", None)
    context.user_data.pop("soda_photo_id", None)
    text = (
        "🔥 <b>КРУТОЙ ЧУВАК</b>\n"
        "<b>ПРЕДЛОЖКА</b>\n"
        "👋 <b>Салам вась!</b>\n\n"
        "Хочешь предложить пост в канал или оценить газяву?\n\n"
        "👇 <b>Выбирай действие:</b>"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "suggest":
        context.user_data.pop("mode", None)
        context.user_data.pop("soda_photo_id", None)
        await query.edit_message_text(
            "📨 <b>ПРЕДЛОЖКА</b>\n"
            "Отправь следующим сообщением текст, фото, видео, GIF, музыку, "
            "стикер или файл.\n\n"
            "После отправки заявка уйдёт модератору.\n\n"
            "🔥 <i>Газуй вась.</i>",
            parse_mode="HTML",
        )

    elif query.data == "soda_rate":
        context.user_data["mode"] = "soda_photo"
        context.user_data.pop("soda_photo_id", None)
        await query.edit_message_text(
            "🥤 <b>ОЦЕНКА ГАЗЯВЫ</b>\n\n"
            "Сначала отправь фото напитка. Если фото нет или не хочешь "
            "его отправлять, нажми кнопку ниже.\n\n"
            "После этого напиши название газировки. Всё отправлю админу.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭ Пропустить фото", callback_data="soda_skip_photo")
            ]]),
        )

    elif query.data == "soda_skip_photo":
        if context.user_data.get("mode") != "soda_photo":
            await query.answer("Сначала выбери «Оценить газяву».", show_alert=True)
            return
        context.user_data["mode"] = "soda_name"
        await query.edit_message_text(
            "✍️ Теперь напиши <b>название газировки</b>.",
            parse_mode="HTML",
        )

    elif query.data == "rules":
        await query.edit_message_text(
            "📜 <b>ПРАВИЛА</b>\n\n"
            "1️⃣ Не спамить.\n\n"
            "2️⃣ Не отправлять незаконный контент.\n\n"
            "3️⃣ Не присылать чужие личные данные.\n\n"
            "4️⃣ Не закидывать одно и то же по несколько раз.\n\n"
            "5️⃣ Администрация оставляет за собой право не публиковать "
            "предложенные материалы.\n\n"
            "💡 <i>Чем интереснее пост, тем выше шанс увидеть его в канале.</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Назад", callback_data="back")
            ]]),
        )

    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ <b>О БОТЕ</b>\n"
            "🤖 Это официальная предложка канала\n"
            "🔥 <b>«Крутой чувак»</b>\n\n"
            "📨 Здесь принимаются предложения от подписчиков.\n\n"
            "👨‍💻 Материалы проходят модерацию.\n\n"
            "⚡ Быстро.\n🔥 Просто.\n😎 По-братски.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Назад", callback_data="back")
            ]]),
        )

    elif query.data == "back":
        context.user_data.pop("mode", None)
        context.user_data.pop("soda_photo_id", None)
        await query.edit_message_text(
            "🔥 <b>КРУТОЙ ЧУВАК ПРЕДЛОЖКА</b>\n\nЧто хочешь намутить?",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )


async def receive_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    mode = context.user_data.get("mode")

    # Отдельный сценарий: оценка газировки
    if mode == "soda_photo":
        if message.photo:
            context.user_data["soda_photo_id"] = message.photo[-1].file_id
            context.user_data["mode"] = "soda_name"
            await message.reply_text(
                "📸 Фото принято! Теперь напиши <b>название газировки</b>.",
                parse_mode="HTML",
            )
        else:
            await message.reply_text(
                "Отправь фото напитка или нажми «Пропустить фото»."
            )
        return

    if mode == "soda_name":
        if not message.text or not message.text.strip():
            await message.reply_text("Напиши название газировки текстом.")
            return

        soda_name = escape(message.text.strip())
        username = (
            f"@{escape(message.from_user.username)}"
            if message.from_user.username
            else "без username"
        )
        admin_text = (
            "🥤 <b>НОВАЯ ОЦЕНКА ГАЗЯВЫ</b>\n\n"
            f"🧃 <b>Название:</b> {soda_name}\n"
            f"👤 <b>Автор:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n\n"
            "Фото приложено, если пользователь его отправил."
        )

        photo_id = context.user_data.get("soda_photo_id")
        if photo_id:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=admin_text,
                parse_mode="HTML",
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                parse_mode="HTML",
            )

        context.user_data.pop("mode", None)
        context.user_data.pop("soda_photo_id", None)
        await message.reply_text(
            "✅ <b>Оценка газявы отправлена админу!</b> Спасибо, вась 🥤",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return

    # Обычная предложка
    username = (
        f"@{escape(message.from_user.username)}"
        if message.from_user.username
        else "без username"
    )
    admin_text = (
        "🔥 <b>НОВАЯ ПРЕДЛОЖКА</b>\n"
        f"👤 <b>Автор:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n\n"
        "👇 <b>Материал ниже.</b>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ОПУБЛИКОВАТЬ", callback_data=f"publish:{message.message_id}")],
        [InlineKeyboardButton("❌ ОТКЛОНИТЬ", callback_data=f"reject:{message.message_id}")],
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML"
    )
    await context.bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=keyboard,
    )
    await message.reply_text(
        "✅ <b>ПРИНЯТО</b>\n"
        "Твоя предложка отправлена на модерацию.\n\n"
        "🔥 Если её одобрят, она появится в канале.\n\n"
        "Васёк спасибец за участие!",
        parse_mode="HTML",
    )


async def moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Вась не мудри.", show_alert=True)
        return

    await query.answer()
    action, message_id = query.data.split(":", 1)

    if action == "publish":
        try:
            await context.bot.copy_message(
                chat_id=CHANNEL_ID,
                from_chat_id=ADMIN_ID,
                message_id=query.message.message_id,
            )
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ <b>ОПУБЛИКОВАНО</b>\nПост успешно отправлен в канал 🔥",
                parse_mode="HTML",
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"❌ Ошибка публикации:\n<code>{escape(str(e))}</code>",
                parse_mode="HTML",
            )

    elif action == "reject":
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="❌ <b>ОТКЛОНЕНО</b>\nПредложка удалена из очереди.",
            parse_mode="HTML",
        )


def main():
    if not TOKEN:
        raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(moderation, pattern=r"^(publish|reject):")
    )
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            (
                filters.TEXT
                | filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.VOICE
                | filters.ANIMATION
                | filters.Document.ALL
                | filters.Sticker.ALL
            ) & ~filters.COMMAND,
            receive_suggestion,
        )
    )
    print("🔥 КРУТОЙ ЧУВАК - ПРЕДЛОЖКА ЗАПУЩЕНА!")
    app.run_polling()


if __name__ == "__main__":
    main()
