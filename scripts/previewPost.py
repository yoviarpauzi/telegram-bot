import os
from telegram import Update, InputMediaPhoto
from telegram.ext import CallbackContext
from scripts.database.userDatabase import isUserHavePost
from scripts.database.userPostDatabase import getUserPost, upsertUserPost
from scripts.database.userImagesDatabase import deleteAllUserImages, upsertUserImages

def delete_images_from_storage(images):
    for image_path in images:
        # Cek apakah file ada dan bukan dari folder /storage/default/
        if os.path.exists(image_path) and not image_path.startswith('storage/default/'):
            try:
                # Hapus file jika berada di luar /storage/default/
                os.remove(image_path)
                print(f"{image_path} berhasil dihapus.")
            except Exception as e:
                print(f"Gagal menghapus {image_path}: {e}")
        else:
            print(f"{image_path} tidak ditemukan di storage atau berada dalam folder default.")

async def show_preview(update:Update, context:CallbackContext) -> None:
    from scripts.handle import start
    users_id = update.callback_query.from_user.id
    images = context.user_data.get('images', [])
    tags = context.user_data.get('tags')
    description = context.user_data.get('description')

    is_user_having_post = isUserHavePost(users_id=users_id)

    if is_user_having_post:
        post_data = getUserPost(users_id=users_id)
        print(post_data)
        photos = post_data.get('images', [])
        deleteAllUserImages(post_data.get('post_id', ''))
        delete_images_from_storage(images=photos)

    # Insert user post and get the post ID
    user_post_id = upsertUserPost(users_id=users_id, tags=tags, description=description)

    # List to hold the image file paths
    image_paths = []

    # Handle image storage, gunakan gambar default jika tidak ada gambar diunggah
    if images:
        # Proses gambar yang diunggah
        for i, image in enumerate(images):
            new_file = await context.bot.get_file(image)
            file_path = f'storage/images/{users_id}_{user_post_id}_{i}.jpg'
            await new_file.download_to_drive(file_path)
            image_paths.append(file_path)
    else:
        # Gunakan gambar default
        if tags == '#girl':
            default_image_path = 'storage/default/girl.jpeg'
        else:
            default_image_path = 'storage/default/boy.jpg'
        
        image_paths.append(default_image_path)

    # Simpan informasi gambar ke dalam database
    upsertUserImages(user_post_id=user_post_id, paths=image_paths)

    # Buat media group untuk ditampilkan sebagai preview
    media_group = [
        InputMediaPhoto(media=open(image_paths[0], 'rb'), caption=f"{tags}\n{description}")
    ]
    media_group.extend([InputMediaPhoto(media=open(image, 'rb')) for image in image_paths[1:]])

    await update.callback_query.message.reply_text('Berikut preview postingan  kamu')
    await update.callback_query.message.reply_media_group(media=media_group)

    # Kembali ke menu awal setelah preview
    await start(update, context)