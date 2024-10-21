import logging
import os
from dotenv import load_dotenv
from scripts.database.createDatabase import createDatabase
from scripts.schedule import schedule_token_reset
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, PreCheckoutQueryHandler, filters
from scripts.handle import start, button_handler, handle_input
from scripts.payment import precheckout_callback, successful_payment_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    load_dotenv()
    API_TOKEN = os.getenv('BOT_TOKEN')

    createDatabase()

    if not os.path.exists('storage/images'):
        os.makedirs('storage/images')

    schedule_token_reset()

    application = ApplicationBuilder().token(API_TOKEN).build()

    # Handlers for bot and payment
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_input))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    application.run_polling()
