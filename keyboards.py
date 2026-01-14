from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 Oylik hisoblash", "📚 Ish rejalar")
    markup.add("📝 Testlar", "📁 Darsliklar")
    markup.add("ℹ️ Ma'lumot", "⚙️ Admin panel")
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]:
        markup.insert(KeyboardButton(s))
    markup.add("⬅️ Orqaga")
    return markup

def toifa_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add("Oliy", "Birinchi", "Ikkinchi", "Mutaxassis")

def yes_no():
    return ReplyKeyboardMarkup(resize_keyboard=True).add("Ha (100%)", "Yo'q")

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 Reklama", "➕ Fayl qo'shish", "⚙️ BHM tahrirlash", "🧹 Tozalash", "🏠 Chiqish")
    return markup
