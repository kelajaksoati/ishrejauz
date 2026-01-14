from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("💰 Oylik hisoblash"), KeyboardButton("📚 Ish rejalar"))
    markup.add(KeyboardButton("📝 Testlar"), KeyboardButton("📁 Darsliklar"))
    markup.add(KeyboardButton("ℹ️ Ma'lumot"), KeyboardButton("⚙️ Admin panel"))
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    subjects = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Biologiya", "Fizika"]
    for s in subjects:
        markup.insert(KeyboardButton(s))
    markup.add(KeyboardButton("⬅️ Orqaga"))
    return markup
