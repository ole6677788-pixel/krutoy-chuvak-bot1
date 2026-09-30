from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (

    Application,

    CommandHandler,

    MessageHandler,

    CallbackQueryHandler,

    ContextTypes,

    filters,

)

# =========================

# НАСТРОЙКИ

# =========================

TOKEN = ""

ADMIN_ID = 6542085968

CHANNEL_ID = -1003076484178

# =========================

# ГЛАВНОЕ МЕНЮ

# =========================

def main_menu():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(

                "📨 Предложить шнягу",

                callback_data="suggest"

            )

        ],

        [

            InlineKeyboardButton(

                "📜 Правила",

                callback_data="rules"

            ),

            InlineKeyboardButton(

                "ℹ️ О боте",

                callback_data="about"

            )

        ]

    ])

# =========================

# /START

# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (


        "🔥 <b>КРУТОЙ ЧУВАК</b>\n"

        "<b>ПРЕДЛОЖКА</b>\n"

        "👋 <b>Салам вась!</b>\n\n"

        "Хочешь предложить пост в канал?\n"

        "Закидывай сюда всё самое интересное:\n\n"
        "🔎 После отправки предложение попадёт "

        "на модерацию.\n\n"

        "👇 <b>Выбирай действие:</b>"

    )

    await update.message.reply_text(

        text,

        parse_mode="HTML",

        reply_markup=main_menu()

    )

# =========================

# КНОПКИ

# =========================

async def buttons(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    query = update.callback_query

    await query.answer()

    # =========================

    # ПРЕДЛОЖИТЬ ПОСТ

    # =========================

    if query.data == "suggest":

        await query.edit_message_text(


            "📨 <b>ПРЕДЛОЖКА</b>\n"


            "Отправь следующим сообщением:\n\n"

            "📝 текст\n"

            "📸 фото\n"

            "🎥 видео\n"

            "🎞 GIF\n"

            "🎵 музыку\n"

            "🎭 стикер\n"

            "📎 файл\n\n"

            "После отправки заявка уйдёт модератору.\n\n"

            "🔥 <i>Газуй вась.</i>",

            

            parse_mode="HTML"

        )

    # =========================

    # ПРАВИЛА

    # =========================

    elif query.data == "rules":

        await query.edit_message_text(


            "📜 <b>ПРАВИЛА</b>\n"


            "1️⃣ Не спамить.\n\n"

            "2️⃣ Не отправлять незаконный контент.\n\n"

            "3️⃣ Не присылать чужие личные данные.\n\n"

            "4️⃣ Не закидывать одно и то же по несколько раз.\n\n"

            "5️⃣ Администрация оставляет за собой "

            "право не публиковать предложенные материалы.\n\n"

            "💡 <i>Васьки а чем интереснее пост - тем выше шанс "

            "увидеть его в канале.</i>",

            

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(

                        "⬅️ Назад",

                        callback_data="back"

                    )

                ]

            ])

        )

    # =========================

    # О БОТЕ

    # =========================

    elif query.data == "about":

        await query.edit_message_text(


            "ℹ️ <b>О БОТЕ</b>\n"


            "🤖 Это официальная предложка канала\n"

            "🔥 <b>«Крутой чувак»</b>\n\n""📨 Здесь принимаются предложения "

            "от подписчиков.\n\n"

            "👨‍💻 Все материалы проходят модерацию.\n\n"

            "⚡ Быстро.\n"

            "🔥 Просто.\n"

            "😎 По-братски.",

            

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(

                        "⬅️ Назад",

                        callback_data="back"

                    )

                ]

            ])

        )

    # =========================

    # НАЗАД

    # =========================

    elif query.data == "back":

        await query.edit_message_text(

            "🔥 <b>КРУТОЙ ЧУВАК ПРЕДЛОЖКА</b>\n\n"

            "Что хочешь намутить?",

            parse_mode="HTML",

            reply_markup=main_menu()

        )

# =========================

# ПРИЁМ ПРЕДЛОЖКИ

# =========================

async def receive_suggestion(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    message = update.message

    username = (

        f"@{message.from_user.username}"

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

        [

            InlineKeyboardButton(

                "✅ ОПУБЛИКОВАТЬ",

                callback_data=f"publish:{message.message_id}"

            )

        ],

        [

            InlineKeyboardButton(

                "❌ ОТКЛОНИТЬ",

                callback_data=f"reject:{message.message_id}"

            )

        ]

    ])

    # Сначала отправляем красивую информацию о заявке

    await context.bot.send_message(

        chat_id=ADMIN_ID,

        text=admin_text,

        parse_mode="HTML"

    )

    # Затем копируем сам материал

    await context.bot.copy_message(

        chat_id=ADMIN_ID,

        from_chat_id=message.chat_id,

        message_id=message.message_id,

        reply_markup=keyboard

    )

    await message.reply_text(


        "✅ <b>ПРИНЯТО</b>\n"


        "Твоя предложка отправлена на модерацию.\n\n"

        "🔥 Вась если её одобрят она появится "

        "в канале, а если нет ну шо паделать вась.\n\n"

        "Васёк спасибец за участие!",

        

        parse_mode="HTML"

    )

# =========================

# МОДЕРАЦИЯ

# =========================

async def moderation(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:

        await query.answer(

            "⛔ Вась не мудри.",

            show_alert=True

        )

        return

    action, message_id = query.data.split(":")

    # =========================

    # ОПУБЛИКОВАТЬ

    # =========================

    if action == "publish":

        try:

            await context.bot.copy_message(

                chat_id=CHANNEL_ID,

                from_chat_id=ADMIN_ID,

                message_id=query.message.message_id

            )

            await query.edit_message_reply_markup(

                reply_markup=None

            )

            await context.bot.send_message(

                chat_id=ADMIN_ID,

                text=(


                    "✅ <b>ОПУБЛИКОВАНО</b>\n"


                    "Пост успешно отправлен в канал 🔥"

                ),

                parse_mode="HTML"

            )

        except Exception as e:

            await context.bot.send_message(

                chat_id=ADMIN_ID,

                text=f"❌ Ошибка публикации:\n<code>{e}</code>",

                parse_mode="HTML"

            )# =========================

    # ОТКЛОНИТЬ

    # =========================

    elif action == "reject":

        await query.edit_message_reply_markup(

            reply_markup=None

        )

        await context.bot.send_message(

            chat_id=ADMIN_ID,

            text=(


                "❌ <b>ОТКЛОНЕНО</b>\n"


                "Предложка удалена из очереди."

            ),

            parse_mode="HTML"

        )

# =========================

# ЗАПУСК

# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(

        CommandHandler("start", start)

    )

    app.add_handler(

        CallbackQueryHandler(

            moderation,

            pattern=r"^(publish|reject):"

        )

    )

    app.add_handler(

        CallbackQueryHandler(buttons)

    )

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

            )

            & ~filters.COMMAND,

            receive_suggestion

        )

    )

    print("🔥 КРУТОЙ ЧУВАК - ПРЕДЛОЖКА ЗАПУЩЕНА!")

    app.run_polling()

main()