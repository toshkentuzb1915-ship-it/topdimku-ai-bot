import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@topdimku_uz"

ADMINS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("⛔ Sizda ruxsat yo‘q.")
        return

    keyboard = [[InlineKeyboardButton(
        "➕ Yangi tovar joylash", callback_data="new"
    )]]

    await update.message.reply_text(
        "🤖 TOPDIMKU AI POST MAKER\n\n"
        "Xush kelibsiz! Reklama yaratish uchun tugmani bosing.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMINS:
        return

    if query.data == "new":
        context.user_data.clear()
        context.user_data["step"] = "photo"
        await query.message.reply_text("📸 Tovar rasmini yuboring.")

    elif query.data == "publish":
        data = context.user_data

        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=data["photo"],
            caption=(
                f"🔥 {data['name']}\n\n"
                f"💰 Narxi: {data['price']}\n"
                f"📞 Telefon: {data['phone']}\n\n"
                f"📝 {data['description']}\n\n"
                "📩 Buyurtma uchun murojaat qiling!\n"
                "📢 @topdimku_uz"
            )
        )

        await query.message.reply_text("✅ Reklama kanalga joylandi!")
        context.user_data.clear()

    elif query.data == "cancel":
        context.user_data.clear()
        await query.message.reply_text("❌ Bekor qilindi.")

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in ADMINS:
        return

    step = context.user_data.get("step")
    message = update.message

    if step == "photo":
        if not message.photo:
            await message.reply_text("Iltimos, rasm yuboring.")
            return
        context.user_data["photo"] = message.photo[-1].file_id
        context.user_data["step"] = "name"
        await message.reply_text("🏷 Tovar nomini yozing.")

    elif step == "name":
        context.user_data["name"] = message.text
        context.user_data["step"] = "price"
        await message.reply_text("💰 Tovar narxini yozing.")

    elif step == "price":
        context.user_data["price"] = message.text
        context.user_data["step"] = "phone"
        await message.reply_text("📞 Telefon raqamini yozing.")

    elif step == "phone":
        context.user_data["phone"] = message.text
        context.user_data["step"] = "description"
        await message.reply_text("📝 Tovar haqida ma'lumot yozing.")

    elif step == "description":
        context.user_data["description"] = message.text
        data = context.user_data

        keyboard = [
            [InlineKeyboardButton("✅ Kanalga joylash", callback_data="publish")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")]
        ]

        await message.reply_photo(
            photo=data["photo"],
            caption=(
                f"🔥 {data['name']}\n\n"
                f"💰 Narxi: {data['price']}\n"
                f"📞 Telefon: {data['phone']}\n\n"
                f"📝 {data['description']}"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["step"] = "confirm"

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(
        filters.PHOTO | (filters.TEXT & ~filters.COMMAND),
        messages
    ))

    app.run_polling()

if __name__ == "__main__":
    main()
