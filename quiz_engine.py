import docx
import fitz  # PyMuPDF
import re
import json
import random
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
            options = json.loads(q[1]) 
            
            formatted_quizzes.append({
                "q": q[0],
                "o": options,
                "a": q[2] # To'g'ri javob ID raqami
            })
            
        random.shuffle(formatted_quizzes)
        return formatted_quizzes

    def parse_quiz_docx(self, file_path):
        """Docx fayldan savol va variantlarni ajratib olish"""
        doc = docx.Document(file_path)
        questions = []
        current_q = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue

            # Savolni aniqlash (1. Savol yoki 1) Savol)
            if re.match(r'^\d+[\. \)]', text):
                if current_q: questions.append(current_q)
                current_q = {'question': text, 'options': [], 'answer': 0}
            
            # Variantni aniqlash (A, B, C yoki D)
            elif re.match(r'^[A-D][\) \.]', text) or re.match(r'^[a-d][\) \.]', text):
                if current_q:
                    is_correct = '*' in text
                    clean_text = text.replace('*', '').strip()
                    # Variant harfini olib tashlash (A) matn -> matn)
                    clean_text = re.sub(r'^[A-Da-d][\) \.]', '', clean_text).strip()
                    
                    if is_correct:
                        current_q['answer'] = len(current_q['options'])
                    current_q['options'].append(clean_text)

        if current_q: questions.append(current_q)
        return questions

    def parse_quiz_pdf(self, file_path):
        """PDF fayldan savollarni qatorlar bo'yicha tahlil qilish"""
        doc = fitz.open(file_path)
        lines = []
        for page in doc:
            text = page.get_text("text")
            lines.extend(text.split('\n'))

        questions = []
        current_q = None

        for line in lines:
            text = line.strip()
            if not text: continue

            if re.match(r'^\d+[\. \)]', text):
                if current_q: questions.append(current_q)
                current_q = {'question': text, 'options': [], 'answer': 0}
            
            elif re.match(r'^[A-D][\) \.]', text) or re.match(r'^[a-d][\) \.]', text):
                if current_q:
                    is_correct = '*' in text
                    clean_text = text.replace('*', '').strip()
                    clean_text = re.sub(r'^[A-Da-d][\) \.]', '', clean_text).strip()
                    if is_correct:
                        current_q['answer'] = len(current_q['options'])
                    current_q['options'].append(clean_text)

        if current_q: questions.append(current_q)
        return questions

    def save_to_db(self, questions, subject):
        """Ajratib olingan savollarni bazaga saqlash"""
        count = 0
        for q in questions:
            if len(q['options']) >= 2: # Kamida 2 ta variant bo'lsa
                self.db.add_quiz(
                    q['question'], 
                    json.dumps(q['options']), 
                    q['answer'], 
                    subject
                )
                count += 1
        return count
