from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

db = Database('ebaza_ultimate.db')

# --- FOYDALANUVCHI MENYULARI ---

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Bazadagi barcha dinamik kategoriyalarni chiqaradi (Ish rejalar, Darsliklar va h.k.)
    categories = db.get_categories()
    for cat in categories:
        markup.insert(KeyboardButton(cat))
    
    # Doimiy funksiyalar
    markup.add("💰 Oylik hisoblash", "📝 Onlayn Test")
    markup.add("📄 Hujjat yaratish", "🤖 AI Yordamchi")
    markup.add("📢 Vakansiyalar", "🎨 Portfolio")
    markup.add("⚙️ Admin panel")
    return markup

def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Oliy", "Birinchi")
    markup.add("Ikkinchi", "Mutaxassis")
    markup.add("O'rta maxsus", "🏠 Bosh menu")
    return markup

def soat_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("10", "15", "18", "20", "25", "30")
    markup.add("🏠 Bosh menu")
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Bazadagi fanlarni dinamik chiqarish
    subjs = db.get_subjects()
    if not subjs: # Agar baza bo'sh bo'lsa, default fanlar
        subjs = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
    
    for s in subjs:
        markup.insert(KeyboardButton(s))
    markup.add("🏠 Bosh menu")
    return markup

def quarter_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    quarters = db.get_quarters()
    for q in quarters:
        markup.insert(KeyboardButton(q))
    markup.add("🏠 Bosh menu")
    return markup

# --- ADMIN MENYULARI ---

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Statistika", "📢 Xabar yuborish")
    markup.add("➕ Kategoriya/Fan/Chorak", "➖ O'chirish (Barcha)")
    markup.add("➕ Fayl qo'shish", "➕ Test qo'shish")
    markup.add("➕ Vakansiya qo'shish", "⚙️ Narxlarni o'zgartirish")
    markup.add("➕ Admin boshqaruvi", "🧹 Bazani tozalash")
    markup.add("🏠 Bosh menu")
    return markup

def settings_menu():
    # Narxlarni o'zgartirish uchun qulay menyu
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("BHM", callback_data="set_bhm"),
        InlineKeyboardButton("Oliy", callback_data="set_oliy"),
        InlineKeyboardButton("1-toifa", callback_data="set_birinchi"),
        InlineKeyboardButton("2-toifa", callback_data="set_ikkinchi"),
        InlineKeyboardButton("Mutaxassis", callback_data="set_mutaxassis")
    )
    return markup

def cat_menu():
    # Fayl qo'shishda kategoriyani tanlash uchun
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for cat in db.get_categories():
        markup.insert(KeyboardButton(cat))
    markup.add("🏠 Bosh menu")
    return markup
