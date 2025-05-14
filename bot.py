import os
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import telegram

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment and constants
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://agni-model.onrender.com/webhook")

if not WEBHOOK_URL.startswith("https://"):
    raise ValueError("WEBHOOK_URL must start with 'https://'")

# Define a basic command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is up and running.")

# Set up the bot application
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))

    # Check existing webhook
    bot: Bot = application.bot
    try:
        current_webhook = await bot.get_webhook_info()
        if current_webhook.url != WEBHOOK_URL:
            logging.info(f"Setting webhook to {WEBHOOK_URL}")
            await bot.set_webhook(url=WEBHOOK_URL)
        else:
            logging.info(f"Webhook already set to {WEBHOOK_URL}")
    except telegram.error.TelegramError as e:
        logging.error(f"Failed to set webhook: {e}")

    logging.info("Bot is ready.")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
