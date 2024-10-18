import sqlite3

def upsertUserImages(user_post_id, paths):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    
    if len(paths) > 3:
        raise ValueError("A post can have a maximum of 3 images.")

    images_data = [(user_post_id, path) for path in paths]

    # Upsert for multiple images
    cur.executemany("""
        INSERT INTO user_images (user_post_id, path)
        VALUES (?, ?)
        ON CONFLICT(id) 
        DO UPDATE SET 
            path = excluded.path
    """, images_data)
    
    conn.commit()
    conn.close()

def deleteAllUserImages(user_post_id): 
     conn = sqlite3.connect('database/database.sqlite')
     cur = conn.cursor()
        
     cur.execute("""
        DELETE FROM user_images
        WHERE user_post_id = ?
     """, (user_post_id,))
    
     conn.commit()
     conn.close()