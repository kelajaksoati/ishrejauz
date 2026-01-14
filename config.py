import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# --- TELEGRAM SOZLAMALARI ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ADMIN_ID ni xavfsiz o'qish (bo'sh yoki xato bo'lsa 0 oladi)
admin_id_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(admin_id_raw) if admin_id_raw and admin_id_raw.isdigit() else 0

# --- AI (GEMINI) KALITLARI ---
# functions.py har xil nomlarni so'rashi mumkinligini hisobga olib, 
# hamma variantlarni bitta o'zgaruvchiga bog'laymiz
raw_ai_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")

GEMINI_API_KEY = raw_ai_key
AI_API_KEY = raw_ai_key    # functions.py dagi 'from config import AI_API_KEY' uchun
OPENAI_API_KEY = raw_ai_key # Eskiroq kodlar uchun

# --- BOT RO'YXATLARI ---
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar"]

# Fanlar ro'yxatini kengaytirilgan variantda qoldirdik
SUBJECTS = [
    "Ona tili", "Adabiyot", "Matematika", "Ingliz tili", 
    "Tarix", "Fizika", "Biologiya", "Kimyo", "Informatika"
]

# --- BAZA SOZLAMALARI ---
DB_NAME = "database.db"
