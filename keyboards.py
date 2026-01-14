from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("💰 Oylik hisoblash"), KeyboardButton("📝 Onlayn Test"))
    markup.add(KeyboardButton("📄 Hujjat yaratish"), KeyboardButton("🤖 AI Yordamchi"))
    markup.add(KeyboardButton("📚 Ish rejalar"), KeyboardButton("📁 Darsliklar"))
    markup.add(KeyboardButton("ℹ️ Ma'lumot"), KeyboardButton("⚙️ Admin panel"))
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjects = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
    for s in subjects:
        markup.insert(KeyboardButton(s))
    markup.add(KeyboardButton("🏠 Asosiy Menu"))
    return markup

def cat_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar")
    markup.add(KeyboardButton("🏠 Chiqish"))
    return markup

def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Oliy", "Birinchi", "Ikkinchi", "Mutaxassis")
    return markup

def yes_no():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Ha", "Yo'q")
    return markup

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 Reklama yuborish", "➕ Fayl qo'shish")
    markup.add("📊 Statistika", "🏠 Chiqish")
    return markup
