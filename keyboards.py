from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

# Bazaga ulanish
db = Database('ebaza_ultimate.db')

# --- 1. YORDAMCHI VA DOIMIY TUGMALAR ---

def back_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

def yes_no_menu():
    # main.py dagi (message.text == "Ha") shartiga moslash uchun
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("Ha"), KeyboardButton("Yo'q"))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 2. FOYDALANUVCHI MENYULARI ---

def main_menu(is_admin=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # A) Avval bazadagi dinamik kategoriyalarni qo'shish
    categories = db.get_categories()
    if categories:
        for cat in categories:
            if cat not in ["📁 Darsliklar", "🎨 Portfolio", "📄 Hujjat yaratish"]:
                markup.insert(KeyboardButton(cat))
    
    # B) Asosiy tugmalar
    markup.row(KeyboardButton("💰 Oylik hisoblash"), KeyboardButton("🤖 AI Yordamchi"))
    markup.row(KeyboardButton("📢 Vakansiyalar"), KeyboardButton("📝 Onlayn Test"))
    markup.row(KeyboardButton("📄 Hujjat yaratish"), KeyboardButton("📁 Darsliklar"))
    markup.row(KeyboardButton("🎨 Portfolio"), KeyboardButton("✍️ Savol yo'llash"))
    
    if is_admin:
        markup.add(KeyboardButton("⚙️ Admin panel"))
        
    return markup

def toifa_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("Oliy"), KeyboardButton("Birinchi"),
        KeyboardButton("Ikkinchi"), KeyboardButton("Mutaxassis"),
        KeyboardButton("🏠 Bosh menu")
    )
    return markup

def subjects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjs = db.get_subjects()
    if subjs:
        for s in subjs:
            markup.insert(KeyboardButton(s))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 3. ADMIN MENYULARI ---

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [
        KeyboardButton("➕ Fayl qo'shish"),
        KeyboardButton("➕ Test qo'shish"), 
        KeyboardButton("➕ Vakansiya qo'shish"),
        KeyboardButton("➕ Kategoriya/Fan/Chorak"), 
        KeyboardButton("📅 O'quv yilini o'zgartirish"),
        KeyboardButton("📊 Statistika"),
        KeyboardButton("📢 Xabar yuborish"), 
        KeyboardButton("⚙️ Narxlarni o'zgartirish"),
        KeyboardButton("🏠 Bosh menu")
    ]
    markup.add(*btns)
    return markup

def settings_menu():
    """Narx, BHM va yangi bo'limlarni o'zgartirish (Moslangan variant)"""
    markup = InlineKeyboardMarkup(row_width=1) # Qulay bo'lishi uchun 1 qatordan
    markup.add(
        InlineKeyboardButton("💰 BHM ni o'zgartirish", callback_data="set_bhm"),
        InlineKeyboardButton("📚 Daftar tekshirish narxi", callback_data="set_daftar"),
        InlineKeyboardButton("🏫 Kabinet mudirligi narxi", callback_data="set_kabinet"),
        InlineKeyboardButton("🎓 Oliy toifa stavkasi", callback_data="set_oliy"),
        InlineKeyboardButton("🥈 1-toifa stavkasi", callback_data="set_birinchi"),
        InlineKeyboardButton("🥉 2-toifa stavkasi", callback_data="set_ikkinchi"),
        InlineKeyboardButton("🎖 Mutaxassis stavkasi", callback_data="set_mutaxassis"),
        InlineKeyboardButton("⬅️ Admin panelga qaytish", callback_data="admin_back")
    )
    return markup

# --- 4. ALOQA (FEEDBACK) ---
def feedback_reply_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✍️ Javob berish", callback_data=f"reply_{user_id}"))
    return markup
