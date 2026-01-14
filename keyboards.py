from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 Oylik hisoblash", "📝 Onlayn Test")
    markup.add("📄 Hujjat yaratish", "🤖 AI Yordamchi")
    markup.add("📚 Ish rejalar", "📁 Darsliklar")
    markup.add("📢 Vakansiyalar", "🎨 Portfolio")
    markup.add("⚙️ Admin panel")
    return markup

def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Oliy", "Birinchi")
    markup.add("Ikkinchi", "Mutaxassis")
    markup.add("O'rta maxsus", "🏠 Bosh menu")
    return markup

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Statistika", "📢 Xabar yuborish")
    markup.add("⚙️ Narxlarni o'zgartirish", "🏠 Bosh menu")
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]:
        markup.insert(KeyboardButton(s))
    markup.add("🏠 Bosh menu")
    return markup

def cat_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar")
    markup.add("🏠 Bosh menu")
    return markup

def soat_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("10", "15", "18", "20", "25", "30")
    markup.add("🏠 Bosh menu")
    return markup
