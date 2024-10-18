from telegram import Update, InputMediaPhoto
from telegram.ext import CallbackContext
from scripts.database.userPostDatabase import getUserPost
import os
import logging

async def send_post_to_community(update: Update, context: CallbackContext, users_id: int):
    post_data = getUserPost(users_id=users_id)

    if not post_data:
        await update.callback_query.message.reply_text("Tidak dapat menemukan postingan untuk pengguna ini.")
        return

    # Ambil chat_id saluran komunitas dari variabel lingkungan
    community_chat_id = os.getenv('CHANNEL_ID')

    bot = context.bot

    # Dapatkan tags, deskripsi, dan gambar dari postingan
    tags = post_data.get('tags', '')
    description = post_data.get('description', '')
    images = post_data.get('images', [])  # Langsung ambil path gambar sebagai list

    if not tags or not description:
        await update.callback_query.message.reply_text("Post data tidak lengkap.")
        return

    # Gabungkan tags dan description menjadi satu string untuk caption
    caption = f"{tags}\n{description}"

    # Pastikan gambar ada dan dapat diakses
    media_group = []
    for idx, image_path in enumerate(images):
        try:
            # Buka file dan tambahkan ke media group
            with open(image_path, 'rb') as img_file:
                if idx == 0:
                    media_group.append(InputMediaPhoto(media=img_file, caption=caption))  # Caption hanya untuk gambar pertama
                else:
                    media_group.append(InputMediaPhoto(media=img_file))
        except FileNotFoundError:
            logging.error(f"File tidak ditemukan: {image_path}")
            await update.callback_query.message.reply_text(f"File gambar {image_path} tidak ditemukan.")
            return

    # Kirim media group atau hanya pesan teks jika tidak ada gambar
    if media_group:
        await bot.send_media_group(chat_id=community_chat_id, media=media_group)
    else:
        await bot.send_message(chat_id=community_chat_id, text=caption)

    # Berikan konfirmasi kepada pengguna
    await update.callback_query.message.reply_text("Postingan Anda telah berhasil dikirim ke saluran komunitas.")