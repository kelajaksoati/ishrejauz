from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Asosiy Menu
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("💰 Oylik hisoblash"), KeyboardButton("📝 Onlayn Test"))
    markup.add(KeyboardButton("📄 Hujjat yaratish"), KeyboardButton("🤖 AI Yordamchi"))
    markup.add(KeyboardButton("📚 Ish rejalar"), KeyboardButton("📁 Darsliklar"))
    markup.add(KeyboardButton("ℹ️ Ma'lumot"), KeyboardButton("⚙️ Admin panel"))
    return markup

# Fanlar menyusi
def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjects = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
    for s in subjects:
        markup.insert(KeyboardButton(s))
    markup.add(KeyboardButton("🏠 Asosiy Menu"))
    return markup

# Toifalar
def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Oliy", "Birinchi", "Ikkinchi", "Mutaxassis")
    return markup

# Ha/Yo'q tanlovi
def yes_no():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Ha", "Yo'q")
    return markup

# Admin Panel Menu
def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 Reklama yuborish", "➕ Fayl qo'shish")
    markup.add("⚙️ BHMni o'zgartirish", "📊 Statistika")
    markup.add("🧹 Bazani tozalash", "🏠 Chiqish")
    return markup

# Test uchun fanlar (Inline)
def test_subjects_inline():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Matematika", callback_data="quiz_matem"),
        InlineKeyboardButton("Pedagogika", callback_data="quiz_pedagog")
    )
    return markup
