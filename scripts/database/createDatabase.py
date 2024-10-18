import sqlite3

def createDatabase(): 
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    # Create the 'users' table (one-to-one relationship with user_post)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            token INTEGER
        )
    """)

    # Create the 'user_post' table with a UNIQUE constraint on users_id to enforce one-to-one relationship
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            users_id INTEGER UNIQUE, 
            tags TEXT,
            description TEXT,
            FOREIGN KEY(users_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create the 'user_images' table for one-to-many relationship with user_post
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_post_id INTEGER,
            path VARCHAR(100),
            FOREIGN KEY(user_post_id) REFERENCES user_post(id) ON DELETE CASCADE
        )
    """)

    conn.commit()  # Save the changes
    conn.close()   # Close the connection