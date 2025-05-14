import os
import json
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.environ.get("7790531310:AAFkK83FK_vqleBZnfGel_JWbKbfqXfKK4w")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CHANNEL_ID = "@agnisinghmodel"

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

def load_media_map():
    try:
        with open("media_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading media_map.json: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send a keyword to get the media.")

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    media_map = load_media_map()

    if prompt in media_map:
        message_id = media_map[prompt]
        try:
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id
            )
        except Exception as e:
            print(f"Error forwarding message: {e}")
            await update.message.reply_text("Error sending the media.")
    else:
        await update.message.reply_text("No media found for that keyword.")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

@app.route('/')
def home():
    return "Bot is online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

if __name__ == '__main__':
    bot.delete_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
