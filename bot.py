import os
import logging
import json
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CHANNEL_ID = "@agnisinghmodel"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def load_media_map():
    try:
        with open("media_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading media_map.json: {e}")
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
            logger.error(f"Error forwarding message: {e}")
            await update.message.reply_text("Error sending the media.")
    else:
        await update.message.reply_text("No media found for that keyword.")

async def set_webhook(application):
    try:
        await application.bot.delete_webhook()
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        logger.info("Webhook set successfully!")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))
    application.post_init = set_webhook
    logger.info("Bot is running...")
    
    # Ensure webhook is used
    application.run_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 8080)), url_path='webhook')
    logger.info("Webhook is listening...")

if __name__ == "__main__":
    main()
