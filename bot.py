import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')

# Initialize Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://checkituser-default-rtdb.firebaseio.com/'
})

# Firebase reference
user_ref = db.reference('users')

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
    }
    user_ref.child(str(user.id)).set(user_data)
    await update.message.reply_text("স্বাগতম! আপনি সফলভাবে রেজিস্টার হয়েছেন।")

# /broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text_to_send = ' '.join(context.args)
        users = user_ref.get()
        if users:
            success = 0
            fail = 0
            for uid, info in users.items():
                try:
                    await context.bot.send_message(chat_id=uid, text=text_to_send)
                    success += 1
                except Exception as e:
                    print(f"Error sending to {uid}: {e}")
                    fail += 1
            await update.message.reply_text(f"✅ মেসেজ পাঠানো হয়েছে!\nসফল: {success} জন\nব্যর্থ: {fail} জন")
        else:
            await update.message.reply_text("⚠️ কোনো ইউজার পাওয়া যায়নি।")
    else:
        await update.message.reply_text("ব্যবহার:\n/broadcast আপনার_মেসেজ")

# /reply command
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("ব্যবহার:\n/reply ইউজার_আইডি আপনার_মেসেজ")
        return
    user_id = context.args[0]
    message = ' '.join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text(f"✅ মেসেজ পাঠানো হয়েছে ইউজার {user_id} কে।")
    except Exception as e:
        await update.message.reply_text(f"⚠️ এরর: {e}")

# Handle normal user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text
    # Save last message (optional future use)
    user_ref.child(str(user.id)).update({
        'last_message': message
    })
    # Optional auto-reply (currently off)
    # await update.message.reply_text("✅ আপনার মেসেজ রিসিভ করা হয়েছে।")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
