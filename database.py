import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            # 1. Foydalanuvchilar
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                full_name TEXT, 
                role TEXT DEFAULT 'user')""")
            
            # 2. Dinamik elementlar (Kategoriya, Fan, Chorak)
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
            
            # 4. Sozlamalar (Oylik hisoblash uchun)
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            
            # 5. Testlar (QuizEngine uchun)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                question TEXT, 
                options TEXT, 
                correct_option_id INTEGER, 
                subject TEXT)""")
            
            # 6. Vakansiyalar
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT, 
                link TEXT)""")

            # 7. Aloqa (Feedback) jadvali - MUKAMMAL QILINDI
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                question TEXT, 
                status TEXT DEFAULT 'new')""")

            # Default sozlamalar
            defaults = [
                ('bhm', '375000'), ('oliy', '5000000'), 
                ('birinchi', '4500000'), ('ikkinchi', '4000000'), 
                ('mutaxassis', '3500000'), ('study_year', '2024-2025')
            ]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

    # --- TESTLAR BILAN ISHLASH ---
    def add_quiz(self, question, options_json, correct_id, subject):
        with self.connection:
            self.cursor.execute("""INSERT INTO quizzes (question, options, correct_option_id, subject) 
                                VALUES (?, ?, ?, ?)""", (question, options_json, correct_id, subject))

    def get_quizzes(self, subject):
        with self.connection:
            return self.cursor.execute(
                "SELECT question, options, correct_option_id FROM quizzes WHERE subject=? ORDER BY RANDOM()", 
                (subject,)
            ).fetchall()

    def delete_subject_quizzes(self, subject):
        with self.connection:
            self.cursor.execute("DELETE FROM quizzes WHERE subject=?", (subject,))

    # --- FOYDALANUVCHILAR ---
    def add_user(self, user_id, full_name=None):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (id, full_name) VALUES (?, ?)", (user_id, full_name))

    def get_all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT id FROM users").fetchall()

    # --- ELEMENTLARNI OLISH ---
    def get_settings(self):
        res = self.cursor.execute("SELECT key, value FROM settings").fetchall()
        return {row[0]: row[1] for row in res}

    def get_categories(self):
        return [r[0] for r in self.cursor.execute("SELECT name FROM categories").fetchall()]

    def get_subjects(self):
        return [r[0] for r in self.cursor.execute("SELECT name FROM subjects").fetchall()]

    def get_quarters(self):
        return [r[0] for r in self.cursor.execute("SELECT name FROM quarters").fetchall()]

    # --- FAYLLAR ---
    def add_file(self, name, f_id, cat, subj, quarter=None):
        with self.connection:
            self.cursor.execute("INSERT INTO files (name, file_id, category, subject, quarter) VALUES (?, ?, ?, ?, ?)", 
                                (name, f_id, cat, subj, quarter))

    def get_files(self, cat, subj, quarter=None):
        if quarter:
            return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=? AND quarter=?", 
                                       (cat, subj, quarter)).fetchall()
        return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=?", 
                                   (cat, subj)).fetchall()

    # --- VAKANSIYALAR ---
    def add_vacancy(self, title, link):
        with self.connection:
            self.cursor.execute("INSERT INTO vacancies (title, link) VALUES (?, ?)", (title, link))

    def get_vacancies(self):
        return self.cursor.execute("SELECT title, link FROM vacancies ORDER BY id DESC").fetchall()

    # --- ALOQA (FEEDBACK) METODLARI ---
    def add_feedback(self, user_id, question):
        """Foydalanuvchi savolini saqlash"""
        with self.connection:
            self.cursor.execute("INSERT INTO feedback (user_id, question) VALUES (?, ?)", (user_id, question))

    def get_new_feedback(self):
        """Hali javob berilmagan savollarni olish"""
        return self.cursor.execute("SELECT * FROM feedback WHERE status='new'").fetchall()

    def update_feedback_status(self, f_id, status='replied'):
        """Savol holatini yangilash (masalan, javob berilgandan so'ng)"""
        with self.connection:
            self.cursor.execute("UPDATE feedback SET status=? WHERE id=?", (status, f_id))

    def __del__(self):
        try: self.connection.close()
        except: pass
