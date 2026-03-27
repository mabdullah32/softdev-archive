import sqlite3
import os

os.makedirs("Data", exist_ok=True)
DB_FILE="Data/data.db"
db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, balance INT, id INTEGER PRIMARY KEY AUTOINCREMENT);")
db.commit()
db.close()

def add_user(username, password):
    DB_NAME = "Data/data.db"
    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()
    DB_CURSOR.execute("SELECT COUNT(*) FROM Users WHERE username = (?)", (username,))
    cursorfetch = DB_CURSOR.fetchone()[0]
    if cursorfetch == 1:
        DB.commit()
        DB.close()
        return False
    DB_CURSOR.execute("INSERT INTO Users VALUES(?, ?, 0, NULL)", (username, password))
    DB.commit()
    DB.close()
    return True

def alter_balance(username, n):
    DB_NAME = "Data/data.db"
    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()
    DB_CURSOR.execute("SELECT COUNT(*) FROM Users WHERE username = (?)", (username,))
    cursorfetch = DB_CURSOR.fetchone()[0]
    if cursorfetch != 1:
        DB.commit()
        DB.close()
        return False
    balance = get_balance(username)
    DB_CURSOR.execute("UPDATE users SET balance = balance + (?) WHERE username = (?)", (n, username))
    DB.commit()
    DB.close()
    return True

def get_balance(username):
    DB_NAME = "Data/data.db"
    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()
    DB_CURSOR.execute("SELECT balance FROM Users WHERE username = (?)",(username,))

    cursorfetch = (DB_CURSOR.fetchone())[0]
    return cursorfetch

def check_password(username, password):
    return password == get_user(username)[1]

def get_user(username):
    DB_NAME = "Data/data.db"
    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()
    DB_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (username,))
    cursorfetch = DB_CURSOR.fetchone()
    return cursorfetch

def get_top_users():
    DB_NAME = "Data/data.db"
    DB = sqlite3.connect(DB_NAME)
    DB_CURSOR = DB.cursor()
    DB_CURSOR.execute("SELECT * FROM Users ORDER BY balance;")
    cursorfetch = DB_CURSOR.fetchall()
    return cursorfetch
