import sqlite3
import json

class Database:
    def __init__(self, db_file):
        # check_same_thread=False aiogram kabi asinxron kutubxonalar uchun zarur
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
            
            # 5. Testlar jadvali (QuizEngine uchun)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                question TEXT, 
                options TEXT, 
                correct_option_id INTEGER, 
                subject TEXT)""")
            
            # 6. Vakansiyalar jadvali
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT, 
                link TEXT)""")

            # --- Boshlang'ich (Default) ma'lumotlarni qo'shish ---
            defaults = [
                ('bhm', '375000'), 
                ('oliy', '5000000'), 
                ('birinchi', '4500000'), 
                ('ikkinchi', '4000000'), 
                ('mutaxassis', '3500000'),
                ('study_year', '2024-2025')
            ]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

            # Dinamik elementlar
            self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", ("Ish reja",))
            self.cursor.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", ("Matematika",))
            self.cursor.execute("INSERT OR IGNORE INTO quarters (name) VALUES (?)", ("1-chorak",))

    # --- TESTLAR (QUIZ) BILAN ISHLASH ---
    def add_quiz(self, question, options_json, correct_id, subject):
        """Yangi test savolini bazaga qo'shish"""
        with self.connection:
            self.cursor.execute("""INSERT INTO quizzes (question, options, correct_option_id, subject) 
                                VALUES (?, ?, ?, ?)""", (question, options_json, correct_id, subject))

    def get_quizzes(self, subject):
        """Fanga tegishli barcha testlarni tasodifiy tartibda olish (random)"""
        with self.connection:
            return self.cursor.execute(
                "SELECT question, options, correct_option_id FROM quizzes WHERE subject=? ORDER BY RANDOM()", 
                (subject,)
            ).fetchall()

    def delete_subject_quizzes(self, subject):
        """Muayyan fanning barcha testlarini tozalash"""
        with self.connection:
            self.cursor.execute("DELETE FROM quizzes WHERE subject=?", (subject,))

    # --- SOZLAMALAR ---
    def get_settings(self):
        with self.connection:
            res = self.cursor.execute("SELECT key, value FROM settings").fetchall()
            return {row[0]: row[1] for row in res}

    def update_setting(self, key, value):
        with self.connection:
            self.cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))

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
            return self.cursor.execute("""SELECT name, file_id FROM files 
                                       WHERE category=? AND subject=?""", 
                                       (cat, subj)).fetchall()

    # --- VAKANSIYALAR ---
    def add_vacancy(self, title, link):
        with self.connection:
            self.cursor.execute("INSERT INTO vacancies (title, link) VALUES (?, ?)", (title, link))

    def get_vacancies(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM vacancies ORDER BY id DESC").fetchall()

    # --- TOZALASH ---
    def clear_all_data(self):
        tables = ['files', 'subjects', 'quizzes', 'categories', 'quarters', 'vacancies']
        with self.connection:
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
