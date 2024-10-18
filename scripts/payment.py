from telegram import Update, LabeledPrice
from telegram.ext import CallbackContext
from scripts.postingPost import send_post_to_community

async def send_invoice(update: Update, context: CallbackContext) -> None:
    await context.bot.send_invoice(
        chat_id=update.callback_query.message.chat.id,
        title='Dating',
        description='Karena token kamu sudah habis, untuk memposting postingan, kamu harus menggift dulu hehehe, support developer bot ini supaya lebih banyak fiturnya:D',
        payload='WPBOT-PYLD',
        currency='XTR',
        prices=[
            LabeledPrice('Basic', 5)
        ],
        provider_token='',  # Make sure to fill in your provider token
    )

async def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload != 'WPBOT-PYLD':
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    print(update.message.successful_payment)
    users_id = update.message.from_user.id
    await send_post_to_community(update=update, context=context, users_id=users_id)