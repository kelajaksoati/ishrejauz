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
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("✅ HA"), KeyboardButton("❌ YO'Q"))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 2. FOYDALANUVCHI MENYULARI ---

def main_menu(is_admin=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # A) Avval bazadagi dinamik kategoriyalarni qo'shish
    categories = db.get_categories()
    if categories:
        for cat in categories:
            if cat not in ["📁 Darsliklar", "🎨 Portfolio"]:
                markup.insert(KeyboardButton(cat))
    
    # B) Asosiy 8 ta tugmani aniq tartibda joylashtirish
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

def quarter_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    quarters = db.get_quarters()
    if quarters:
        for q in quarters:
            markup.insert(KeyboardButton(q))
    markup.add(KeyboardButton("🏠 Bosh menu"))
    return markup

# --- 3. TEST (QUIZ) UCHUN TUGMALAR ---

def quiz_answer_menu(correct_id, options_count=3):
    markup = InlineKeyboardMarkup(row_width=options_count)
    labels = ["A", "B", "C", "D", "E"]
    btns = []
    
    for i in range(options_count):
        btns.append(InlineKeyboardButton(
            labels[i], 
            callback_data=f"quiz_ans_{i}_{correct_id}"
        ))
    
    markup.add(*btns)
    markup.add(InlineKeyboardButton("❌ Testni yakunlash", callback_data="quiz_stop"))
    return markup

# --- 4. ADMIN MENYULARI ---

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
    """Narx, BHM va boshqa ustamalarni o'zgartirish (Siz so'ragan yangi variant)"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💰 BHMni o'zgartirish", callback_data="set_bhm"),
        InlineKeyboardButton("📚 Daftar tekshirish", callback_data="set_daftar"),
        InlineKeyboardButton("🏫 Kabinet mudirligi", callback_data="set_kabinet"),
        InlineKeyboardButton("🎓 Oliy toifa", callback_data="set_oliy"),
        InlineKeyboardButton("🥈 1-toifa", callback_data="set_birinchi"),
        InlineKeyboardButton("🥉 2-toifa", callback_data="set_ikkinchi"),
        InlineKeyboardButton("🎖 Mutaxassis", callback_data="set_mutaxassis")
    )
    return markup

# --- 5. ALOQA (FEEDBACK) UCHUN ADMIN TUGMASI ---

def feedback_reply_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✍️ Javob berish", callback_data=f"reply_{user_id}"))
    return markup
