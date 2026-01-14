from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 Oylik hisoblash", "📚 Ish rejalar")
    markup.add("📝 Testlar", "📁 Darsliklar")
    markup.add("ℹ️ Ma'lumot", "⚙️ Admin panel")
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjects = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
    for s in subjects:
        markup.insert(KeyboardButton(s))
    markup.add("⬅️ Orqaga")
    return markup

def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Oliy", "Birinchi", "Ikkinchi", "Mutaxassis")
    return markup

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 Reklama", "➕ Fayl qo'shish", "⚙️ BHM tahrirlash", "🧹 Tozalash", "🏠 Chiqish")
    return markup
