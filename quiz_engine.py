import random
import json
from database import Database

class QuizEngine:
    def __init__(self):
        # Bazaga ulanish
        self.db = Database('ebaza_ultimate.db')

    def get_quiz(self, subject):
        """Bazadan berilgan fan bo'yicha testlarni oladi va formatlaydi"""
        raw_quizzes = self.db.get_quizzes(subject)
        
        if not raw_quizzes:
            return []

        formatted_quizzes = []
        for q in raw_quizzes:
            # q[0] - savol, q[1] - variantlar (JSON string), q[2] - to'g'ri javob ID
            options = json.loads(q[1]) # Stringni ro'yxatga aylantiramiz
            
            formatted_quizzes.append({
                "q": q[0],
                "o": options,
                "a": options[q[2]] # To'g'ri javob matni
            })
            
        # Savollar har safar har xil tartibda chiqishi uchun
        random.shuffle(formatted_quizzes)
        return formatted_quizzes
