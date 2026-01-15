import sqlite3

class Database:
    def __init__(self, db_file):
        # check_same_thread=False aiogram kabi asinxron kutubxonalar bilan ishlashda xatolik oldini oladi
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
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
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            
            # --- Boshlang'ich (Default) ma'lumotlarni qo'shish ---
            
            # Oylik sozlamalari
            defaults = [
                ('bhm', '375000'), 
                ('oliy', '5000000'), 
                ('birinchi', '4500000'), 
                ('ikkinchi', '4000000'), 
                ('mutaxassis', '3500000'),
                ('study_year', '2024-2025') # O'quv yili default holati
            ]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

            # Siz so'ragan boshlang'ich dinamik ma'lumotlar
            self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", ("Ish reja",))
            self.cursor.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", ("Matematika",))
            self.cursor.execute("INSERT OR IGNORE INTO quarters (name) VALUES (?)", ("1-chorak",))

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

    # --- SOZLAMALAR ---
    def get_settings(self):
        with self.connection:
            res = self.cursor.execute("SELECT key, value FROM settings").fetchall()
            return {row[0]: row[1] for row in res}

    # --- FOYDALANUVCHILAR ---
    def add_user(self, user_id, full_name=None):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (id, full_name) VALUES (?, ?)", (user_id, full_name))

    def get_users_count(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(id) FROM users").fetchone()[0]

    # --- UNIVERSAL ELEMENTLAR (Kategoriya, Fan, Chorak) ---
    def add_item(self, table, column, value):
        with self.connection:
            self.cursor.execute(f"INSERT OR IGNORE INTO {table} ({column}) VALUES (?)", (value,))

    def delete_item(self, table, column, value):
        with self.connection:
            self.cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (value,))

    def get_categories(self):
        res = self.cursor.execute("SELECT name FROM categories").fetchall()
        return [r[0] for r in res]

    def get_subjects(self):
        res = self.cursor.execute("SELECT name FROM subjects").fetchall()
        return [r[0] for r in res]

    def get_quarters(self):
        res = self.cursor.execute("SELECT name FROM quarters").fetchall()
        return [r[0] for r in res]

    # --- FAYLLAR ---
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
            return self.cursor.fetchall()

    # --- VAKANSIYALAR ---
    def add_vacancy(self, title, link):
        with self.connection:
            self.cursor.execute("INSERT INTO vacancies (title, link) VALUES (?, ?)", (title, link))

    def get_vacancies(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM vacancies ORDER BY id DESC")
            return self.cursor.fetchall()

    # --- TOZALASH VA STATISTIKA ---
    def clear_all_data(self):
        """Muhim jadvallarni tozalash (Admin uchun)"""
        tables = ['files', 'subjects', 'quizzes', 'categories', 'quarters', 'vacancies']
        with self.connection:
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")

    def __del__(self):
        self.connection.close()
