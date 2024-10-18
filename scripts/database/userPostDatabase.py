import sqlite3

def upsertUserPost(users_id, tags, description):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()

    # Menggunakan INSERT dengan ON CONFLICT untuk memperbarui data jika users_id sudah ada
    cur.execute("""
        INSERT INTO user_post (users_id, tags, description)
        VALUES (?, ?, ?)
        ON CONFLICT(users_id) 
        DO UPDATE SET 
            tags = excluded.tags,
            description = excluded.description
    """, (users_id, tags, description))

    # Jika data dimasukkan (tidak ada konflik), lastrowid akan berisi ID baru
    if cur.lastrowid:
        post_id = cur.lastrowid
    else:
        # Jika terjadi konflik, kita ambil ID dari baris yang ada
        cur.execute("SELECT id FROM user_post WHERE users_id = ?", (users_id,))
        post_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return post_id

def getUserPost(users_id):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    
    # Query to select post details for the given user
    cur.execute("""
        SELECT up.id, up.tags, up.description
        FROM user_post up
        WHERE up.users_id = ?
    """, (users_id,))
    
    # Fetch the post data
    post = cur.fetchone()

    if post:
        post_id, tags, description = post

        # Query to select image paths for the given post
        cur.execute("""
            SELECT path
            FROM user_images
            WHERE user_post_id = ?
        """, (post_id,))
        
        # Fetch all image paths
        images = [row[0] for row in cur.fetchall()]

        result = {
            "post_id": post_id,
            "tags": tags,
            "description": description,
            "images": images
        }
    else:
        result = None  # If the user has no post

    conn.close()
    
    return result