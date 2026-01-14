import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, full_name TEXT, role TEXT DEFAULT 'user')")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, category TEXT, subject TEXT)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
            
            defaults = [('bhm', 375000), ('oliy', 5000000), ('birinchi', 4500000), ('ikkinchi', 4000000), ('mutaxassis', 3500000)]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))

    # --- ADMIN BOSHQARUVI UCHUN ---
    def set_role(self, user_id, role):
        with self.connection:
            self.cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))

    def get_admins(self):
        with self.connection:
            return self.cursor.execute("SELECT id FROM users WHERE role = 'admin'").fetchall()

    def is_admin(self, user_id, main_admin_id):
        if user_id == main_admin_id: return True
        with self.connection:
            res = self.cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
            return res and res[0] == 'admin'
    # ------------------------------

    def add_file(self, name, f_id, cat, subj):
        with self.connection:
            self.cursor.execute("INSERT INTO files (name, file_id, category, subject) VALUES (?, ?, ?, ?)", (name, f_id, cat, subj))

    def get_files(self, cat, subj):
        with self.connection:
            return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=?", (cat, subj)).fetchall()

    def get_setting(self, key):
        with self.connection:
            res = self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return res[0] if res else 0

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT id FROM users").fetchall()
