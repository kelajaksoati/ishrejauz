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
            if len(q['options']) >= 2:
                self.db.add_quiz(
                    q['question'], 
                    json.dumps(q['options']), 
                    q['answer'], 
                    subject
                )
                count += 1
        return count

    def get_test_result(self, user_answers, correct_answers):
        """
        Natijani hisoblash va batafsil hisobot shakllantirish.
        user_answers: [0, 1, 2...] (ID lar ro'yxati)
        correct_answers: [{'q': '...', 'o': [...], 'a': 0}, ...]
        """
        score = 0
        total = len(correct_answers)
        if total == 0: return "Siz hali test topshirmadingiz."
        
        report = "📊 **Test natijalari:**\n\n"

        for i, (u_ans, c_data) in enumerate(zip(user_answers, correct_answers), 1):
            correct_id = c_data['a']
            options = c_data['o']
            
            # Xatolikdan qochish uchun tekshiruv
            try:
                user_ans_text = options[u_ans]
                correct_ans_text = options[correct_id]
            except IndexError:
                user_ans_text = "Noma'lum"
                correct_ans_text = options[correct_id]

            if u_ans == correct_id:
                score += 1
                report += f"{i}. ✅ To'g'ri\n"
            else:
                report += f"{i}. ❌ Xato\n   └ Siz: `{user_ans_text}`\n   └ To'g'ri: `{correct_ans_text}`\n"

        foiz = (score / total) * 100
        report += f"\n---"
        report += f"\n✅ To'g'ri javoblar: {score}"
        report += f"\n❌ Xato javoblar: {total - score}"
        report += f"\n📈 Umumiy natija: **{foiz:.1f}%**"

        return report
