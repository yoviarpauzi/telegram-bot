import telegram
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from scripts.database.userDatabase import insertOrIgnoreUser
from scripts.payment import send_invoice
from scripts.database.userDatabase import updateTokenUser, getUser
from scripts.database.userDatabase import isUserHavePost
from scripts.postingPost import send_post_to_community
from scripts.createPost import handle_image_upload, handle_finish_upload, handle_tags, handle_description, handle_username_choice, move_to_tags, handle_tags_choice

async def handle_input(update: Update, context: CallbackContext) -> None:
    state = context.user_data.get('state')

    state_handler = {
        'awaiting_image': handle_image_upload,
        'awaiting_finish_upload': handle_finish_upload,
        'awaiting_tags': handle_tags,
        'awaiting_description': handle_description,
        'awaiting_username_choice': handle_username_choice
    }

    if state in state_handler:
        await state_handler[state](update, context)
    else:
        await update.message.reply_text("Silakan pilih 'Buat Postingan' terlebih dahulu.")

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    try:
        await query.answer()
    except telegram.error.BadRequest as e:
        logging.error(f"Error answering callback query: {e}")
        return

    if query.data == 'create_post':
        # Pilihan untuk unggah gambar atau langsung buat tag
        keyboard = [
            [
                InlineKeyboardButton("Unggah Gambar", callback_data='upload_image'),
                InlineKeyboardButton("Langsung Buat Tag", callback_data='skip_image')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Apakah Anda ingin mengunggah gambar untuk postingan Anda?", reply_markup=reply_markup)

    elif query.data == 'upload_image':
        context.user_data['state'] = 'awaiting_image'
        context.user_data['images'] = []
        await query.message.reply_text("Silakan unggah gambar Anda terlebih dahulu.")
        
    elif query.data == 'skip_image':
        if 'images' not in context.user_data:
            context.user_data['images'] = []
        await move_to_tags(update, context)
    
    elif query.data in ['add_username_yes', 'add_username_no']:
        await handle_username_choice(update, context)

    elif query.data in ['tag_boy', 'tag_girl']:
        await handle_tags_choice(update, context)

    elif query.data == 'posting_post':
        users_id = update.callback_query.from_user.id
        is_user_have_post = isUserHavePost(users_id=users_id)
        if not is_user_have_post:
            keyboard = [
                [InlineKeyboardButton("Buat Postingan", callback_data='create_post')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "Tidak ada postingan yang ditemukan. Silakan buat postingan terlebih dahulu.",
                reply_markup=reply_markup
            )
            return
        else:
            await query.message.reply_text("Anda memilih untuk memposting postingan.")
            user = getUser(users_id)
            if user[1] == 0:
                await query.message.reply_text("Maaf token anda sudah habis untuk memposting postingan hari ini, coba lagi besok hari:D")
            else:
                updateTokenUser(users_id=users_id, token=user[1] - 1)
                await send_post_to_community(update=update, context=context, users_id=users_id)

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Buat Postingan", callback_data='create_post'),
            InlineKeyboardButton("Posting Postingan", callback_data='posting_post')
        ],
        [
            InlineKeyboardButton(
                "Beli Telegram Star",
                url="https://t.me/Delingger?text=Hi%20saya%20mau%20beli%20Telegram%20Star"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        users_id = update.message.from_user.id
        await update.message.reply_text(
            'Selamat datang di dating bot, kamu bisa membuat postingan, dan posting postingan kamu supaya bisa dilihat oleh publik. Atau, kamu bisa membeli telegram star.',
            reply_markup=reply_markup
        )
    elif update.callback_query:
        users_id = update.callback_query.from_user.id
        await update.callback_query.message.reply_text(
            'Selamat datang di dating bot, kamu bisa membuat postingan, dan posting postingan kamu supaya bisa dilihat oleh publik. Atau, kamu bisa membeli telegram star.',
            reply_markup=reply_markup
        )
    
    insertOrIgnoreUser(users_id=users_id)