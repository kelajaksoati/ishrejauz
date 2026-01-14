class QuizEngine:
    def __init__(self):
        self.questions = {
            "Matematika": [
                {"q": "2+2*2=?", "o": ["6", "8", "4"], "a": "6"},
                {"q": "Ildiz ostida 16?", "o": ["4", "8", "2"], "a": "4"}
            ],
            "Pedagogika": [
                {"q": "Ta'limning asosi nima?", "o": ["Tarbiyaviy", "Bilim", "Dars"], "a": "Bilim"}
            ]
        }

    def get_questions(self, subject):
        return self.questions.get(subject, [])
