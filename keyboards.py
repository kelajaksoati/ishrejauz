from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

# Bazaga ulanish (Dinamik tugmalar uchun)
db = Database('ebaza_ultimate.db')

# --- 1. YORDAMCHI VA DOIMIY TUGMALAR ---

def back_menu():
    """Orqaga qaytish va Bosh menu tugmasi"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

def yes_no_menu():
    """Ha/Yo'q tanlovi uchun (Oylik hisoblashda ishlatiladi)"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ HA"), KeyboardButton("❌ YO'Q"))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 2. FOYDALANUVCHI MENYULARI ---

def main_menu(is_admin=False):
    """
    Asosiy menyu: Kategoriya va xizmatlar.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Bazadagi dinamik kategoriyalar (Ish rejalar, Darsliklar va h.k.)
    categories = db.get_categories()
    if categories:
        for cat in categories:
            markup.insert(KeyboardButton(cat))
    
    # Asosiy xizmatlar
    markup.add("💰 Oylik hisoblash", "📝 Onlayn Test")
    markup.add("📄 Hujjat yaratish", "🤖 AI Yordamchi")
    markup.add("📢 Vakansiyalar", "🎨 Portfolio")
    
    # Admin bo'lsa, sozlamalar tugmasini qo'shish
    if is_admin:
        markup.add("⚙️ Admin panel")
        
    return markup

def toifa_menu():
    """Oylik hisoblash uchun toifalar"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Oliy", "Birinchi")
    markup.add("Ikkinchi", "Mutaxassis")
    markup.add("O'rta maxsus", "🏠 Bosh menu")
    return markup

def subjects_menu():
    """Fanlar ro'yxati (Baza yoki Default)"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjs = db.get_subjects()
    if not subjs:
        subjs = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
    
    for s in subjs:
        markup.insert(KeyboardButton(s))
    markup.add("🏠 Bosh menu")
    return markup

def quarter_menu():
    """Choraklar uchun"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    quarters = db.get_quarters()
    for q in quarters:
        markup.insert(KeyboardButton(q))
    markup.add("🏠 Bosh menu")
    return markup

# --- 3. ADMIN MENYULARI ---

def admin_menu():
    """Admin boshqaruv paneli"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Statistika", "📢 Xabar yuborish")
    markup.add("➕ Kategoriya/Fan/Chorak", "➕ Fayl qo'shish")
    markup.add("➕ Test qo'shish", "➕ Vakansiya qo'shish")
    markup.add("⚙️ Narxlarni o'zgartirish", "🧹 Bazani tozalash")
    markup.add("🏠 Bosh menu")
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
