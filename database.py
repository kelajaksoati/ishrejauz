import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.setup()

    def setup(self):
        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, category TEXT, subject TEXT)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
            # BHM va stavkalarni kiritish
            self.cursor.execute("INSERT OR IGNORE INTO settings VALUES ('bhm', 375000)")

    def add_file(self, name, file_id, category, subject):
        with self.connection:
            return self.cursor.execute("INSERT INTO files (name, file_id, category, subject) VALUES (?, ?, ?, ?)", (name, file_id, category, subject))

    def get_files(self, category, subject):
        with self.connection:
            return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=?", (category, subject)).fetchall()
