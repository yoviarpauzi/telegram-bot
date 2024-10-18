import sqlite3

def insertOrIgnoreUser(users_id, token=3):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    
    # Use INSERT OR IGNORE to insert user if not exists
    cur.execute("""
        INSERT OR IGNORE INTO users (id,  token)
        VALUES (?, ?)
    """, (users_id, token))

    # Commit the changes to ensure the new user is inserted
    conn.commit()
    conn.close()

def updateTokenUser(users_id, token):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()

    # Update token for the user
    cur.execute("""
        UPDATE users
        SET token = ?
        WHERE id = ?
    """, (token, users_id))

    conn.commit()
    conn.close()

def resetTokensForAllUsers(default_token=3):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE users
        SET token = ?
        WHERE token < ?
    """, (default_token,default_token))

    conn.commit()
    conn.close()

def getUser(users_id):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM users WHERE id = ?
    """, (users_id,))

    user = cur.fetchone()

    cur.close()

    return user

def isUserHavePost(users_id):
    conn = sqlite3.connect('database/database.sqlite')
    cur = conn.cursor()
    
    # Query to check if user has a post
    cur.execute("""
        SELECT COUNT(*)
        FROM user_post
        WHERE users_id = ?
    """, (users_id,))
    
    # Fetch result
    count = cur.fetchone()[0]
    
    # Close the connection
    conn.close()
    
    # Return True if count is greater than 0, otherwise False
    return count > 0