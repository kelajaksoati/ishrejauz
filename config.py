import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Kategoriyalar
CATEGORIES = ["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar", "📢 Vakansiyalar"]
SUBJECTS = ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"]
