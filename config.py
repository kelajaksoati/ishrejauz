import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# --- TELEGRAM SOZLAMALARI ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ADMIN_ID ni xavfsiz o'qish
admin_id_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(admin_id_raw) if admin_id_raw and admin_id_raw.isdigit() else 0

# --- AI (GEMINI) KALITLARI ---
raw_ai_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")
AI_API_KEY = raw_ai_key if raw_ai_key else None
GEMINI_API_KEY = AI_API_KEY

# --- BAZA NOMINI O'ZGARTIRISH ---
# main.py da 'ebaza_ultimate.db' ishlatganimiz uchun shu yerda ham moslaymiz
DB_NAME = "ebaza_ultimate.db"

# --- OYLIK HISOBLASH UCHUN STANDART QIYMATLAR ---
# Agar bazada ma'lumot bo'lmasa, ushbu standartlardan foydalaniladi
DEFAULT_SETTINGS = {
    "bhm": 375000,
    "oliy": 4500000,
    "birinchi": 4000000,
    "ikkinchi": 3600000,
    "mutaxassis": 3200000,
    "daftar": 180000,
    "kabinet": 180000,
    "study_year": "2024-2025"
}

# --- RO'YXATLAR ---
# Bu ro'yxatlarni bot ishlash jarayonida dinamik kengaytirish mumkin
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar", "💰 Oylik hisoblash"]

SUBJECTS = [
    "Ona tili", "Adabiyot", "Matematika", "Ingliz tili", 
    "Tarix", "Fizika", "Biologiya", "Kimyo", "Informatika", "Geografiya"
]
