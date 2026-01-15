import docx
import fitz  # PyMuPDF
import re
import json
import random
import os
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
            try:
                # Bazadan kelgan JSON stringni listga o'tkazamiz
                options = json.loads(q[1]) 
                formatted_quizzes.append({
                    "q": q[0],
                    "o": options,
                    "a": q[2] # To'g'ri javob ID raqami (0, 1, 2...)
                })
            except Exception as e:
                print(f"JSON yuklashda xato: {e}")
                continue
            
        random.shuffle(formatted_quizzes)
        # Odatda bitta test sessiyasi uchun 20-30 ta savol kifoya
        return formatted_quizzes[:30] 

    def _clean_text(self, text, pattern):
        """Matndan ortiqcha harf va raqamlarni tozalash"""
        clean = re.sub(pattern, '', text).replace('*', '').strip()
        return clean

    def parse_quiz_docx(self, file_path):
        """Docx fayldan savol va variantlarni ajratib olish"""
        doc = docx.Document(file_path)
        questions = []
        current_q = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue

            # Savolni aniqlash (Masalan: "1. Savol matni")
            if re.match(r'^\d+[\. \)]', text):
                if current_q and len(current_q['options']) >= 2:
                    questions.append(current_q)
                
                q_text = self._clean_text(text, r'^\d+[\. \)]')
                current_q = {'question': q_text, 'options': [], 'answer': 0}
            
            # Variantlarni aniqlash (Masalan: "A) Variant" yoki "A. Variant")
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

    def parse_quiz_pdf(self, file_path):
        """PDF fayldan savollarni tahlil qilish"""
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
                if current_q and len(current_q['options']) >= 2:
                    questions.append(current_q)
                
                q_text = self._clean_text(text, r'^\d+[\. \)]')
                current_q = {'question': q_text, 'options': [], 'answer': 0}
            
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

    def save_to_db(self, questions, subject):
        """Ajratib olingan savollarni bazaga saqlash"""
        count = 0
        for q in questions:
            # Kamida 2 ta variant bo'lsa saqlaymiz
            if len(q['options']) >= 2:
                self.db.add_quiz(
                    q['question'], 
                    json.dumps(q['options'], ensure_ascii=False), 
                    q['answer'], 
                    subject
                )
                count += 1
        return count

    def get_test_result(self, user_answers, quiz_list):
        """Natijani hisoblash va batafsil hisobot shakllantirish"""
        score = 0
        total = len(quiz_list)
        if total == 0: return "Siz hali test topshirmadingiz."
        
        report = "📊 **Test natijalari:**\n\n"

        for i, (u_ans, q_data) in enumerate(zip(user_answers, quiz_list), 1):
            correct_id = q_data['a']
            options = q_data['o']
            
            try:
                user_ans_text = options[u_ans]
                correct_ans_text = options[correct_id]
            except (IndexError, TypeError):
                user_ans_text = "Noma'lum"
                correct_ans_text = options[correct_id]

            if u_ans == correct_id:
                score += 1
                report += f"{i}. ✅ To'g'ri\n"
            else:
                report += f"{i}. ❌ Xato\n   └ Siz: `{user_ans_text}`\n   └ To'g'ri: `{correct_ans_text}`\n"

        foiz = (score / total) * 100
        report += f"\n---"
        report += f"\n✅ To'g'ri: {score}"
        report += f"\n❌ Xato: {total - score}"
        report += f"\n📈 Umumiy natija: **{foiz:.1f}%**"

        return report
