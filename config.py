import os
from dotenv import load_dotenv

load_dotenv()

# Telegram sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ADMIN_ID ni xavfsiz o'qish (bo'sh bo'lsa 0 oladi, xato bermaydi)
admin_id_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(admin_id_raw) if admin_id_raw and admin_id_raw.isdigit() else 0

# AI Kaliti - functions.py aynan GEMINI_API_KEY nomini talab qilmoqda
# Ikkala variantni ham tekshiradigan qilib sozladik
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = GEMINI_API_KEY # Eskisiga ham moslik uchun

# Kategoriyalar va Fanlar
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar"]
SUBJECTS = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
