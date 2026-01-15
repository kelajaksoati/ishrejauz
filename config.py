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
# Barcha turdagi chaqiruvlar uchun yagona kalit tizimi
raw_ai_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")

GEMINI_API_KEY = raw_ai_key
AI_API_KEY = raw_ai_key     # functions.py dagi 'from config import AI_API_KEY' uchun

# --- BOT RO'YXATLARI ---
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar"]

SUBJECTS = [
    "Ona tili", "Adabiyot", "Matematika", "Ingliz tili", 
    "Tarix", "Fizika", "Biologiya", "Kimyo", "Informatika"
]

# --- BAZA SOZLAMALARI ---
DB_NAME = "ebaza_ultimate.db" # Database.py dagi nom bilan bir xil bo'lishi kerak
