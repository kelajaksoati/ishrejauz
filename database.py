import sqlite3
import json

class Database:
    def __init__(self, db_file):
        # check_same_thread=False asinxron aiogram uchun juda muhim
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            # 1. Foydalanuvchilar va Analitika
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                full_name TEXT, 
                role TEXT DEFAULT 'user',
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS activity_logs (
                user_id INTEGER, 
                section TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
            # 2. Fayllar tizimi (Darsliklar va ish rejalar)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                file_id TEXT, 
                category TEXT, 
                subject TEXT, 
                quarter TEXT DEFAULT '1')""")
            
            # 3. Sozlamalar (Oylik stavkalari va BHM)
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            
            # 4. Testlar va Natijalar (Sertifikat uchun barcha maydonlar bilan)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                question TEXT, 
                options TEXT, 
                answer INTEGER, 
                subject TEXT)""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                name TEXT, 
                subject TEXT, 
                score INTEGER, 
                time_spent INTEGER, 
                date DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
            # 5. Vakansiyalar (Kengaytirilgan variant)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                muassasa TEXT, 
                manzil TEXT, 
                fan TEXT, 
                soat TEXT, 
                sharoit TEXT, 
                aloqa TEXT,
                date DATETIME DEFAULT CURRENT_TIMESTAMP)""")

            # 6. Feedback (Aloqa)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                question TEXT, 
                status TEXT DEFAULT 'new')""")

            # Standart sozlamalar
            defaults = [
                ('bhm', '375000'), ('oliy', '5000000'), 
                ('birinchi', '4500000'), ('ikkinchi', '4000000'), 
                ('mutaxassis', '3500000'), ('daftar', '110000'), 
                ('kabinet', '110000'), ('study_year', '2024-2025')
            ]
            self.cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?)", defaults)

    # --- ANALITIKA VA FOYDALANUVCHI ---
    def add_user(self, user_id, full_name=None):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (id, full_name) VALUES (?, ?)", (user_id, full_name))

    def add_activity(self, user_id, section):
        with self.connection:
            self.cursor.execute("INSERT INTO activity_logs (user_id, section) VALUES (?, ?)", (user_id, section))

    def get_stats(self):
        total_users = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        most_active = self.cursor.execute("""SELECT section, COUNT(*) as c 
                                          FROM activity_logs GROUP BY section 
                                          ORDER BY c DESC LIMIT 1""").fetchone()
        return total_users, most_active

    def is_admin(self, user_id):
        res = self.cursor.execute("SELECT role FROM users WHERE id=?", (user_id,)).fetchone()
        return res[0] == 'admin' if res else False

    def set_role(self, user_id, role):
        with self.connection:
            self.cursor.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))

    # --- SOZLAMALAR ---
    def get_settings(self):
        res = self.cursor.execute("SELECT key, value FROM settings").fetchall()
        return {row[0]: row[1] for row in res}

    def update_setting(self, key, value):
        with self.connection:
            self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    # --- FAYLLAR (ISH REJA VA DARSLIK) ---
    def add_file(self, name, f_id, cat, subj, quarter='1'):
        with self.connection:
            self.cursor.execute("INSERT INTO files (name, file_id, category, subject, quarter) VALUES (?, ?, ?, ?, ?)", 
                                (name, f_id, cat, subj, quarter))

    def get_files(self, cat, subj, quarter='1'):
        return self.cursor.execute("SELECT name, file_id FROM files WHERE category=? AND subject=? AND quarter=?", 
                                   (cat, subj, quarter)).fetchall()

    # --- TEST TIZIMI ---
    def add_quiz(self, q, o, a, s):
        with self.connection:
            self.cursor.execute("INSERT INTO quizzes (question, options, answer, subject) VALUES (?, ?, ?, ?)", (q, o, a, s))

    def get_quizzes(self, subject):
        return self.cursor.execute("SELECT question, options, answer FROM quizzes WHERE subject=? ORDER BY RANDOM()", (subject,)).fetchall()

    def add_test_result(self, u_id, name, subj, score, time_s=0):
        with self.connection:
            self.cursor.execute("INSERT INTO test_results (user_id, name, subject, score, time_spent) VALUES (?,?,?,?,?)",
                                (u_id, name, subj, score, time_s))

    def get_top_rating(self):
        return self.cursor.execute("SELECT name, score, subject FROM test_results ORDER BY score DESC, time_spent ASC LIMIT 10").fetchall()

    # --- VAKANSIYALAR ---
    def add_vacancy(self, u_id, muassasa, manzil, fan, soat, sharoit, aloqa):
        with self.connection:
            self.cursor.execute("""INSERT INTO vacancies (user_id, muassasa, manzil, fan, soat, sharoit, aloqa) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)""", (u_id, muassasa, manzil, fan, soat, sharoit, aloqa))

    def get_vacancies(self):
        return self.cursor.execute("SELECT muassasa, manzil, fan, soat, sharoit, aloqa FROM vacancies ORDER BY id DESC").fetchall()

    # --- FEEDBACK ---
    def add_feedback(self, user_id, question):
        with self.connection:
            self.cursor.execute("INSERT INTO feedback (user_id, question) VALUES (?, ?)", (user_id, question))

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
