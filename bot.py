import os
import json
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., https://your-app.onrender.com
CHANNEL_ID = "@agnisinghmodel"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load media map
def load_media_map():
    try:
        with open("media_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading media_map.json: {e}")
        return {}

# Command handlers
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
            logger.error(f"Error forwarding message: {e}")
            await update.message.reply_text("Error sending the media.")
    else:
        await update.message.reply_text("No media found for that keyword.")

# Create Flask app
app = Flask(__name__)
application = None  # Placeholder for the bot app

@app.route('/')
def home():
    return 'Bot is alive.'

@app.route('/webhook', methods=['POST'])
def webhook():
    if application:
        update = Update.de_json(request.get_json(force=True), application.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
    return 'OK'

# Main bot setup
async def set_webhook():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logger.info("Webhook set successfully.")

def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    # Set webhook asynchronously
    asyncio.run(set_webhook())

if __name__ == '__main__':
    main()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
