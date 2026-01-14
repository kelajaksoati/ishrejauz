import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            # 1. Foydalanuvchilar jadvali
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                full_name TEXT, 
                role TEXT DEFAULT 'user')""")
            
            # 2. Kategoriyalar, Fanlar va Choraklar
            self.cursor.execute("CREATE TABLE IF NOT EXISTS categories (name TEXT PRIMARY KEY)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS subjects (name TEXT PRIMARY KEY)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS quarters (name TEXT PRIMARY KEY)")
            
            # 3. Fayllar jadvali
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                file_id TEXT, 
                category TEXT, 
                subject TEXT, 
                quarter TEXT)""")
            
            # 4. Sozlamalar jadvali
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
            
            defaults = [
                ('bhm', 375000), 
                ('oliy', 5000000), 
                ('birinchi', 4500000), 
                ('ikkinchi', 4000000), 
                ('mutaxassis', 3500000)
            ]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

            # 5. Testlar va Vakansiyalar jadvali
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                question TEXT, 
                options TEXT, 
                correct_option_id INTEGER, 
                subject TEXT)""")
            
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT, 
                link TEXT)""")

    # --- UNIVERSAL FUNKSIYA (Siz so'ragan) ---
    def get_items(self, table_name):
        """Berilgan jadvaldagi barcha ma'lumotlarni qaytaradi"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()

    # --- FOYDALANUVCHI VA ADMIN BOSHQARUVI ---
    def add_user(self, user_id, full_name=None):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (id, full_name) VALUES (?, ?)", (user_id, full_name))

    def set_role(self, user_id, role):
        with self.connection:
            self.cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))

    def is_admin(self, user_id, main_admin_id):
        if str(user_id) == str(main_admin_id): return True
        with self.connection:
            res = self.cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
            return res and res[0] == 'admin'

    def get_users_count(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(id) FROM users").fetchone()[0]

    # --- UNIVERSAL QO'SHISH VA O'CHIRISH ---
    def add_item(self, table, column, value):
        with self.connection:
            self.cursor.execute(f"INSERT OR IGNORE INTO {table} ({column}) VALUES (?)", (value,))

    def delete_item(self, table, column, value):
        with self.connection:
            self.cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (value,))

    # --- FAYLLAR BILAN ISHLASH ---
    def add_file(self, name, f_id, cat, subj, quarter=None):
        with self.connection:
            self.cursor.execute("""INSERT INTO files (name, file_id, category, subject, quarter) 
                                VALUES (?, ?, ?, ?, ?)""", (name, f_id, cat, subj, quarter))

    def get_files(self, cat, subj, quarter=None):
        with self.connection:
            if quarter:
                return self.cursor.execute("""SELECT name, file_id FROM files 
                                           WHERE category=? AND subject=? AND quarter=?""", 
                                           (cat, subj, quarter)).fetchall()
            return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=?", 
                                       (cat, subj)).fetchall()

    # --- SOZLAMALAR (OYLIK UCHUN) ---
    def update_setting(self, key, value):
        with self.connection:
            self.cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))

    def get_setting(self, key):
        with self.connection:
            res = self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return res[0] if res else 0

    # --- DINAMIK RO'YXATLARNI OLISH ---
    def get_categories(self):
        res = self.cursor.execute("SELECT name FROM categories").fetchall()
        return [r[0] for r in res]

    def get_subjects(self):
        res = self.cursor.execute("SELECT name FROM subjects").fetchall()
        return [r[0] for r in res]

    def get_quarters(self):
        res = self.cursor.execute("SELECT name FROM quarters").fetchall()
        return [r[0] for r in res]

    # --- BAZANI TOZALASH ---
    def clear_all_data(self):
        tables = ['files', 'subjects', 'quizzes', 'categories', 'quarters', 'vacancies']
        with self.connection:
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")
