import docx
import fitz  # PyMuPDF
import re
import json
import random
import os
from database import Database
from config import DB_NAME

class QuizEngine:
    def __init__(self):
        # config.py dagi DB_NAME ni ishlatamiz
        self.db = Database(DB_NAME)

    def get_quiz(self, subject):
        """Bazadan testlarni oladi va aralashtiradi"""
        raw_quizzes = self.db.get_quizzes(subject)
        
        if not raw_quizzes:
            return []

        formatted_quizzes = []
        for q in raw_quizzes:
            try:
                # q[0] - savol, q[1] - options (JSON), q[2] - answer ID
                options = json.loads(q[1]) 
                formatted_quizzes.append({
                    "q": q[0],
                    "o": options,
                    "a": q[2] 
                })
            except Exception as e:
                continue
            
        random.shuffle(formatted_quizzes)
        # Ultra: Test sifatli bo'lishi uchun 20-30 ta savol yetarli
        return formatted_quizzes[:25] 

    def _clean_text(self, text, pattern):
        """Ortiqcha belgilarni tozalash"""
        clean = re.sub(pattern, '', text).replace('*', '').strip()
        return clean

    # --- PARSERLAR (DOCX & PDF) ---
    def parse_quiz_docx(self, file_path):
        doc = docx.Document(file_path)
        questions = []
        current_q = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue

            # Savol: 1. Matn
            if re.match(r'^\d+[\. \)]', text):
                if current_q and len(current_q['options']) >= 2:
                    questions.append(current_q)
                
                q_text = self._clean_text(text, r'^\d+[\. \)]')
                current_q = {'question': q_text, 'options': [], 'answer': 0}
            
            # Variant: A) Matn (To'g'risi * bilan)
            elif re.match(r'^[A-Da-d][\) \.]', text):
                if current_q:
                    is_correct = '*' in text
                    opt_text = self._clean_text(text, r'^[A-Da-d][\) \.]')
                    
                    if is_correct:
                        current_q['answer'] = len(current_q['options'])
                    current_q['options'].append(opt_text)

        if current_q and len(current_q['options']) >= 2:
            questions.append(current_q)
        return questions

    # --- NATIJANI HISOBLASH ---
    def calculate_final_score(self, user_answers, quiz_list):
        """
        Natijani hisoblaydi.
        Qaytaradi: (foiz_integer, report_text)
        """
        score = 0
        total = len(quiz_list)
        if total == 0: return 0, "Test topilmadi."
        
        report = "📊 **Test natijalari:**\n\n"

        for i, (u_ans, q_data) in enumerate(zip(user_answers, quiz_list), 1):
            correct_id = q_data['a']
            options = q_data['o']
            
            if u_ans == correct_id:
                score += 1
                report += f"{i}. ✅\n"
            else:
                correct_text = options[correct_id]
                report += f"{i}. ❌ (To'g'ri: {correct_text})\n"

        foiz = int((score / total) * 100)
        report += f"\n---\n✅ To'g'ri: {score}/{total}\n📈 Natija: **{foiz}%**"

        return foiz, report

    def save_to_db(self, questions, subject):
        """Testlarni bazaga quyish"""
        count = 0
        for q in questions:
            if len(q['options']) >= 2:
                self.db.add_quiz(
                    q['question'], 
                    json.dumps(q['options'], ensure_ascii=False), 
                    q['answer'], 
                    subject
                )
                count += 1
        return count
