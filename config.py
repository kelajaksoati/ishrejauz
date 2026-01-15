import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# --- TELEGRAM SOZLAMALARI ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ADMIN_ID ni xavfsiz o'qish (bo'sh bo'lsa 0 qaytaradi)
admin_id_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(admin_id_raw) if admin_id_raw and admin_id_raw.isdigit() else 0

# --- AI (GEMINI) KALITLARI ---
# .env dan o'qish (har xil nomlarni tekshiradi)
raw_ai_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")

# Agar kalit topilmasa, bot qulab tushmasligi uchun tekshiruv
if not raw_ai_key:
    print("⚠️ DIQQAT: AI API kaliti topilmadi! .env faylini tekshiring.")
    AI_API_KEY = None 
else:
    AI_API_KEY = raw_ai_key

GEMINI_API_KEY = AI_API_KEY

# --- BOT RO'YXATLARI ---
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar"]

SUBJECTS = [
    "Ona tili", "Adabiyot", "Matematika", "Ingliz tili", 
    "Tarix", "Fizika", "Biologiya", "Kimyo", "Informatika"
]

# --- BAZA SOZLAMALARI ---
# Diqqat: database.py faylingizda qaysi nom ishlatilgan bo'lsa shuni yozing
DB_NAME = "database.db"
