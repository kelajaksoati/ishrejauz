class QuizEngine:
    def __init__(self):
        self.data = {
            "Matematika": [
                {"q": "Sin(90) nechaga teng?", "o": ["0", "1", "0.5"], "a": "1"},
                {"q": "2x2*2=?", "o": ["8", "6", "4"], "a": "8"}
            ],
            "Pedagogika": [
                {"q": "Didaktika nima?", "o": ["O'qitish nazariyasi", "Tarbiya", "Fan"], "a": "O'qitish nazariyasi"}
            ]
        }

    def get_quiz(self, subject):
        return self.data.get(subject, [])
