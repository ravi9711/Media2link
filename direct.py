import json, os, uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = "8209473593:AAFGFR0BUgL8hGDaPG2Uvv1U1-5YA_kTR2U"  # replace with your bot token
BOT_USERNAME = "Linkifyxmediabot"
ADMIN_ID = 8363966106  # replace with your Telegram user ID
UPLOAD_FILE = "uploads.json"

# === Helper Functions ===
def load_uploads():
    return json.load(open(UPLOAD_FILE)) if os.path.exists(UPLOAD_FILE) else {}

def save_uploads(data):
    with open(UPLOAD_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        key = args[0]
        uploads = load_uploads()
        if key in uploads:
            file_data = uploads[key]
            file_type, file_id, caption = file_data["type"], file_data["file_id"], file_data.get("caption", "")
            if file_type == "photo":
                await update.message.reply_photo(file_id, caption=caption)
            elif file_type == "video":
                await update.message.reply_video(file_id, caption=caption)
            return

    keyboard = [
        [InlineKeyboardButton("📤 Upload", callback_data="upload")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ox1_spark"),
         InlineKeyboardButton("🔔 Updates", callback_data="updates")],
        [InlineKeyboardButton("🤖 Dev Special Bots", callback_data="devbots")],
        [InlineKeyboardButton("🌐 Community 🗿", url="https://t.me/+ANPRnHyYFuI1MGZl")]
    ]
    await update.message.reply_text(
        "👋 *Welcome to LinkifyX Media Bot*\nChoose an option below 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# === Button Handler ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload":
        await query.message.reply_text("📸 Send me any *photo* or *video* to get your unique link!", parse_mode="Markdown")
        context.user_data["awaiting_upload"] = True

    elif query.data == "updates":
        await query.message.reply_video("https://files.catbox.moe/2rh9jm.mp4", caption="Any issue? DM me 💬 @ox1_spark")

    elif query.data == "devbots":
        photo = "https://files.catbox.moe/5lm6cc.jpg"
        btn = [[InlineKeyboardButton("🌐 Community 🗿", url="https://t.me/+ANPRnHyYFuI1MGZl")]]
        await query.message.reply_photo(photo, caption="⚙️ Here are my special dev bots 👇", reply_markup=InlineKeyboardMarkup(btn))

# === Media Upload ===
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_upload"):
        return

    file_id, file_type = None, None
    caption = update.message.caption or ""

    if update.message.photo:
        file_id, file_type = update.message.photo[-1].file_id, "photo"
    elif update.message.video:
        file_id, file_type = update.message.video.file_id, "video"
    else:
        await update.message.reply_text("❌ Only photo/video supported.")
        return

    key = str(uuid.uuid4())
    uploads = load_uploads()
    uploads[key] = {"type": file_type, "file_id": file_id, "caption": caption}
    save_uploads(uploads)

    link = f"https://t.me/{BOT_USERNAME}?start={key}"
    await update.message.reply_text(f"✅ *Uploaded Successfully!*\n\n🔗 Your Link:\n{link}", parse_mode="Markdown")
    context.user_data["awaiting_upload"] = False

# === Broadcast System ===
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    await update.message.reply_text("❗ *Enter Your Message To Broadcast*", parse_mode="Markdown")
    context.user_data["awaiting_broadcast"] = True

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_broadcast"):
        return
    text = update.message.text
    users = [ADMIN_ID]  # add more user IDs later
    for u in users:
        try:
            await context.bot.send_message(chat_id=u, text=text, parse_mode="HTML")
        except:
            pass
    await update.message.reply_text("🔁 <b>Broadcast sent!</b>", parse_mode="HTML")
    context.user_data["awaiting_broadcast"] = False

# === Main ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()