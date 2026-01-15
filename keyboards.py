from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

# Bazaga ulanish
db = Database('ebaza_ultimate.db')

# --- 1. YORDAMCHI VA DOIMIY TUGMALAR ---

def back_menu():
    """Orqaga qaytish va Bosh menu tugmasi"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

def yes_no_menu():
    """Ha/Yo'q tanlovi"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("✅ HA"), KeyboardButton("❌ YO'Q"))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 2. FOYDALANUVCHI MENYULARI ---

def main_menu(is_admin=False):
    """Asosiy menyu: Dinamik kategoriyalar va xizmatlar"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # 1. Bazadagi dinamik kategoriyalar (Ish rejalar, Darsliklar va h.k.)
    categories = db.get_categories()
    if categories:
        for cat in categories:
            markup.insert(KeyboardButton(cat))
    
    # 2. Asosiy xizmatlar
    markup.add(KeyboardButton("💰 Oylik hisoblash"), KeyboardButton("🤖 AI Yordamchi"))
    markup.add(KeyboardButton("📢 Vakansiyalar"), KeyboardButton("📝 Onlayn Test"))
    
    # Admin bo'lsa, admin panel tugmasini qo'shish
    if is_admin:
        markup.add(KeyboardButton("⚙️ Admin panel"))
        
    return markup

def toifa_menu():
    """Oylik hisoblash uchun toifalar"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("Oliy"), KeyboardButton("Birinchi"),
        KeyboardButton("Ikkinchi"), KeyboardButton("Mutaxassis"),
        KeyboardButton("🏠 Bosh menu")
    )
    return markup

def subjects_menu():
    """Fanlar ro'yxati (Bazadan)"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjs = db.get_subjects()
    if subjs:
        for s in subjs:
            markup.insert(KeyboardButton(s))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

def quarter_menu():
    """Choraklar (Bazadan dinamik)"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    quarters = db.get_quarters()
    if quarters:
        for q in quarters:
            markup.insert(KeyboardButton(q))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 3. ADMIN MENYULARI ---

def admin_menu():
    """Admin boshqaruv paneli"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [
        KeyboardButton("➕ Fayl qo'shish"),
        KeyboardButton("➕ Vakansiya qo'shish"),
        KeyboardButton("📅 O'quv yilini o'zgartirish"),
        KeyboardButton("🔢 Choraklarni boshqarish"),
        KeyboardButton("📊 Statistika"),
        KeyboardButton("⚙️ Narxlarni o'zgartirish"),
        KeyboardButton("🏠 Bosh menu")
    ]
    markup.add(*btns)
    return markup

def settings_menu():
    """Narx va BHM sozlamalari (Inline)"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💰 BHM", callback_data="set_bhm"),
        InlineKeyboardButton("🎓 Oliy", callback_data="set_oliy"),
        InlineKeyboardButton("🥈 1-toifa", callback_data="set_birinchi"),
        InlineKeyboardButton("🥉 2-toifa", callback_data="set_ikkinchi"),
        InlineKeyboardButton("🎖 Mutaxassis", callback_data="set_mutaxassis")
    )
    return markup
