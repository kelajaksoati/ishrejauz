import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, category TEXT, subject TEXT)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
            
            # Oylik stavkalari (Hukumat qarorlariga asosan bazaviy qiymatlar)
            defaults = [('bhm', 375000), ('oliy', 5000000), ('birinchi', 4500000), 
                        ('ikkinchi', 4000000), ('mutaxassis', 3500000)]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT id FROM users").fetchall()

    def add_file(self, name, file_id, category, subject):
        with self.connection:
            return self.cursor.execute("INSERT INTO files (name, file_id, category, subject) VALUES (?, ?, ?, ?)", (name, file_id, category, subject))

    def get_files(self, category, subject):
        with self.connection:
            return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=?", (category, subject)).fetchall()

    def update_setting(self, key, value):
        with self.connection:
            return self.cursor.execute("UPDATE settings SET value=? WHERE key=?", (value, key))

    def get_setting(self, key):
        with self.connection:
            res = self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return res[0] if res else 0

    def clean_db(self):
        with self.connection:
            return self.cursor.execute("DELETE FROM users")
