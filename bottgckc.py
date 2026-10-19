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

SODA_RATINGS = {
    "soda_fire": ("🔥", "Ахуенная", "7–10"),
    "soda_mid": ("🤔", "50/50", "4–6",),
    "soda_trash": ("🗑️", "Хуйня", "1–3"),
    "soda_vasiliev": ("🗿", "Для Васильева", "деревня"),
}


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Предложить шнягу", callback_data="suggest")],
        [InlineKeyboardButton("🥤 Оценить газяву", callback_data="soda_rate")],
        [
            InlineKeyboardButton("📜 Правила", callback_data="rules"),
            InlineKeyboardButton("ℹ️ О боте", callback_data="about"),
        ],
    ])


def rating_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Ахуенная (7–10)", callback_data="soda_fire")],
        [InlineKeyboardButton("🤔 50/50 (попробовать чёто новое, 4–6)", callback_data="soda_mid")],
        [InlineKeyboardButton("🗑️ Хуйня (лишняя трата бабла, 1–3)", callback_data="soda_trash")],
        [InlineKeyboardButton("🗿 Для Васильева (деревня)", callback_data="soda_vasiliev")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back")],
    ])


def back_keyboard(callback_data="soda_back_rating"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⬅️ Назад", callback_data=callback_data)
    ]])


async def show_rating_menu(query, context):
    context.user_data["mode"] = "soda_rating"
    context.user_data.pop("soda_rating", None)
    context.user_data.pop("soda_name", None)
    context.user_data.pop("soda_photo_id", None)
    await query.edit_message_text(
        "🥤 <b>ОЦЕНКА ГАЗЯВЫ</b>\n\n"
        "Выбирай вердикт для энчика:",
        parse_mode="HTML",
        reply_markup=rating_keyboard(),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("mode", None)
    context.user_data.pop("soda_rating", None)
    context.user_data.pop("soda_name", None)
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
    data = query.data

    if data == "suggest":
        context.user_data.pop("mode", None)
        context.user_data.pop("soda_rating", None)
        context.user_data.pop("soda_name", None)
        context.user_data.pop("soda_photo_id", None)
        await query.edit_message_text(
            "📨 <b>ПРЕДЛОЖКА</b>\n"
            "Отправь следующим сообщением текст, фото, видео, GIF, музыку, "
            "стикер или файл.\n\n"
            "После отправки заявка уйдёт модератору.\n\n"
            "🔥 <i>Газуй вась.</i>",
            parse_mode="HTML",
            reply_markup=back_keyboard("back"),
        )

    elif data == "soda_rate":
        await show_rating_menu(query, context)

    elif data in SODA_RATINGS:
        context.user_data["soda_rating"] = data
        context.user_data["mode"] = "soda_name"
        context.user_data.pop("soda_name", None)
        context.user_data.pop("soda_photo_id", None)
        emoji, title, score = SODA_RATINGS[data]
        await query.edit_message_text(
            f"{emoji} <b>Выбрано: {escape(title)} ({escape(score)})</b>\n\n"
            "✍️ Теперь напиши название газявы (энчика).",
            parse_mode="HTML",
            reply_markup=back_keyboard(),
        )

    elif data == "soda_back_rating":
        await show_rating_menu(query, context)

    elif data == "soda_add_photo":
        if context.user_data.get("mode") != "soda_photo_choice":
            await query.answer("Сначала выбери оценку газявы.", show_alert=True)
            return
        context.user_data["mode"] = "soda_photo"
        await query.edit_message_text(
            "📸 Отправь фото газявы одним сообщением.\n\n"
            "Если передумал, можешь вернуться назад.",
            reply_markup=back_keyboard("soda_back_photo_choice"),
        )

    elif data == "soda_skip_photo":
        if context.user_data.get("mode") != "soda_photo_choice":
            await query.answer("Этот шаг уже завершён.", show_alert=True)
            return
        await send_soda_to_admin(query, context)

    elif data == "soda_back_photo_choice":
        context.user_data["mode"] = "soda_name"
        await query.edit_message_text(
            "✍️ Напиши название газявы (энчика).",
            reply_markup=back_keyboard(),
        )

    elif data == "rules":
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
            reply_markup=back_keyboard("back"),
        )

    elif data == "about":
        await query.edit_message_text(
            "ℹ️ <b>О БОТЕ</b>\n"
            "🤖 Это официальная предложка канала\n"
            "🔥 <b>«Крутой чувак»</b>\n\n"
            "📨 Здесь принимаются предложения от подписчиков.\n\n"
            "👨‍💻 Материалы проходят модерацию.\n\n"
            "⚡ Быстро.\n🔥 Просто.\n😎 По-братски.",
            parse_mode="HTML",
            reply_markup=back_keyboard("back"),
        )

    elif data == "back":
        context.user_data.pop("mode", None)
        context.user_data.pop("soda_rating", None)
        context.user_data.pop("soda_name", None)
        context.user_data.pop("soda_photo_id", None)
        await query.edit_message_text(
            "🔥 <b>КРУТОЙ ЧУВАК ПРЕДЛОЖКА</b>\n\nЧто хочешь намутить?",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )


async def send_soda_to_admin(query, context):
    user = query.from_user
    rating_key = context.user_data.get("soda_rating")
    rating = SODA_RATINGS.get(rating_key)
    soda_name = context.user_data.get("soda_name")
    if not rating or not soda_name:
        await query.answer("Не хватает данных. Начни оценку заново.", show_alert=True)
        return

    emoji, title, score = rating
    username = f"@{escape(user.username)}" if user.username else "без username"
    admin_text = (
        "🥤 <b>НОВАЯ ОЦЕНКА ГАЗЯВЫ</b>\n\n"
        f"🧃 <b>Название:</b> {escape(soda_name)}\n"
        f"🏆 <b>Оценка:</b> {emoji} {escape(title)} ({escape(score)})\n"
        f"👤 <b>Автор:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>"
    )
    photo_id = context.user_data.get("soda_photo_id")
    if photo_id:
        await context.bot.send_photo(
            chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML"
        )

    context.user_data.pop("mode", None)
    context.user_data.pop("soda_rating", None)
    context.user_data.pop("soda_name", None)
    context.user_data.pop("soda_photo_id", None)
    await context.bot.send_message(
        chat_id=user.id,
        text="✅ <b>Оценка газявы отправлена админу!</b> Спасибо, вась 🥤",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


async def receive_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    mode = context.user_data.get("mode")

    if mode == "soda_name":
        if not message.text or not message.text.strip():
            await message.reply_text(
                "Напиши название газявы текстом.",
                reply_markup=back_keyboard(),
            )
            return
        context.user_data["soda_name"] = message.text.strip()
        context.user_data["mode"] = "soda_photo_choice"
        await message.reply_text(
            "📸 Хочешь приложить фото энчика? Это необязательно.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 Добавить фото", callback_data="soda_add_photo")],
                [InlineKeyboardButton("⏭ Отправить без фото", callback_data="soda_skip_photo")],
                [InlineKeyboardButton("⬅️ Назад к названию", callback_data="soda_back_photo_choice")],
            ]),
        )
        return

    if mode == "soda_photo":
        if message.photo:
            context.user_data["soda_photo_id"] = message.photo[-1].file_id
            rating = SODA_RATINGS.get(context.user_data.get("soda_rating"))
            if not rating or not context.user_data.get("soda_name"):
                await message.reply_text("Что-то потерялось. Начни оценку заново через меню.")
                context.user_data.pop("mode", None)
                return
            emoji, title, score = rating
            username = f"@{escape(message.from_user.username)}" if message.from_user.username else "без username"
            admin_text = (
                "🥤 <b>НОВАЯ ОЦЕНКА ГАЗЯВЫ</b>\n\n"
                f"🧃 <b>Название:</b> {escape(context.user_data['soda_name'])}\n"
                f"🏆 <b>Оценка:</b> {emoji} {escape(title)} ({escape(score)})\n"
                f"👤 <b>Автор:</b> {username}\n"
                f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>"
            )
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=admin_text,
                parse_mode="HTML",
            )
            context.user_data.pop("mode", None)
            context.user_data.pop("soda_rating", None)
            context.user_data.pop("soda_name", None)
            context.user_data.pop("soda_photo_id", None)
            await message.reply_text(
                "✅ <b>Оценка газявы с фото отправлена админу!</b> Спасибо, вась 🥤",
                parse_mode="HTML",
                reply_markup=main_menu(),
            )
        else:
            await message.reply_text(
                "Отправь фото одним сообщением или нажми «Назад».",
                reply_markup=back_keyboard("soda_back_photo_choice"),
            )
        return

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
