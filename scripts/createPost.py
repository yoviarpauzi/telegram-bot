from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from scripts.database.userDatabase import isUserHavePost
from scripts.database.userPostDatabase import getUserPost, upsertUserPost
from scripts.database.userImagesDatabase import deleteAllUserImages, upsertUserImages
from scripts.previewPost import show_preview

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

async def handle_image_upload(update: Update, context: CallbackContext) -> None:
    if update.message.photo:
        image_file_id = update.message.photo[-1].file_id
        context.user_data['images'].append(image_file_id)

        uploaded_count = len(context.user_data['images'])
        await update.message.reply_text(f"Gambar diterima! Anda telah mengunggah {uploaded_count} gambar.")

        if uploaded_count < 3:
            await update.message.reply_text("Apakah Anda ingin mengupload gambar lagi? (Ya/Tidak)")
            context.user_data['state'] = 'awaiting_finish_upload'
        else:
            await move_to_tags(update, context)
    else:
        await update.message.reply_text("Harap unggah gambar terlebih dahulu.")

async def handle_finish_upload(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        if update.message.text.lower() in ['Tidak', 'tidak', 'No', 'no']:
            await move_to_tags(update, context)
        elif update.message.text.lower() in ['Ya', 'ya', 'Iya', 'iya', 'Yes', 'yes']:
            context.user_data['state'] = 'awaiting_image'
            await update.message.reply_text("Silakan unggah gambar Anda lagi.")
        else:
            await update.message.reply_text("Silakan jawab dengan 'Ya' atau 'Tidak'.")
    else:
        await update.message.reply_text("Harap kirimkan teks yang valid.")

async def move_to_tags(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'awaiting_tags'

    # Menggunakan update.callback_query.message untuk callback query
    message = update.message or update.callback_query.message  # Menangani baik dari message atau callback query
    uploaded_count = len(context.user_data['images'])
    
    await message.reply_text(f"Anda telah mengunggah {uploaded_count} gambar.")
    
    # Keyboard untuk memilih tag
    keyboard = [
        [InlineKeyboardButton("Boy", callback_data='tag_boy'),
        InlineKeyboardButton("Girl", callback_data='tag_girl')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Silakan pilih tag untuk postingan Anda:", reply_markup=reply_markup)

async def handle_tags(update: Update, context: CallbackContext) -> None:
    context.user_data['tags'] = update.message.text
    context.user_data['state'] = 'awaiting_description'
    await update.message.reply_text("Tag diterima!")
    await update.message.reply_text("Sekarang silakan masukkan deskripsi untuk postingan Anda.")

async def handle_tags_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Jawab callback query untuk menghindari masalah kedaluwarsa

    if query.data == 'tag_boy':
        context.user_data['tags'] = '#boy'
    elif query.data == 'tag_girl':
        context.user_data['tags'] = '#girl'

    context.user_data['state'] = 'awaiting_description'
    await query.message.reply_text("Tag diterima! Sekarang silakan masukkan deskripsi untuk postingan Anda.")

async def handle_description(update: Update, context: CallbackContext) -> None:
    context.user_data['description'] = update.message.text
    context.user_data['state'] = 'awaiting_username_choice'

    keyboard = [
        [InlineKeyboardButton("Ya", callback_data='add_username_yes'),
        InlineKeyboardButton("Tidak", callback_data='add_username_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Apakah Anda ingin menambahkan username ke postingan Anda?", reply_markup=reply_markup)

async def handle_username_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Dapatkan query dari callback
    await query.answer()  # Menjawab callback query untuk menghindari masalah kedaluwarsa

    # Periksa data yang dipilih oleh pengguna melalui callback_data
    if query.data == 'add_username_yes':
        username = query.from_user.username  # Ambil username dari user
        if username:
            context.user_data['description'] += f"\nPosted by @{username}"
        else:
            await query.message.reply_text("Username Anda tidak tersedia.")

    # Lanjutkan ke preview setelah pemilihan username atau tidak
    await show_preview(update, context)