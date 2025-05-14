import os
import json
import logging
import asyncio
from threading import Thread
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., https://your-app.onrender.com
CHANNEL_ID = "@agnisinghmodel"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load media map from JSON
def load_media_map():
    try:
        with open("media_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading media_map.json: {e}")
        return {}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send a keyword to get the media.")

# Handle keyword messages
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

# Flask app setup
app = Flask(__name__)
application = None  # Telegram bot application

@app.route('/')
def home():
    return 'Bot is alive.'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        incoming_data = request.get_json(force=True)
        logger.info(f"Received data: {incoming_data}")

        if application:
            update = Update.de_json(incoming_data, application.bot)
            Thread(target=asyncio.run, args=(application.process_update(update),)).start()

        return 'OK'
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return 'Error', 500

# Set webhook with logging
async def set_webhook():
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL environment variable is not set!")
        return

    url = f"{WEBHOOK_URL}/webhook"
    try:
        logger.info("Deleting old webhook (if any)...")
        await application.bot.delete_webhook()

        logger.info(f"Setting new webhook to: {url}")
        success = await application.bot.set_webhook(url)

        if success:
            logger.info("Webhook set successfully.")
        else:
            logger.error("Failed to set webhook. Telegram API returned False.")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")

# Bot initialization
def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    asyncio.run(set_webhook())

if __name__ == '__main__':
    main()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
