import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

# Gemini API ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

async def get_ai_answer(query):
    """Google Gemini orqali metodik yordam olish"""
    try:
        # Xavfsizlik sozlamalari (javob to'xtab qolmasligi uchun)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=safety_settings
        )
        
        prompt = (
            "Siz o'zbekistonlik o'qituvchilarga yordam beruvchi tajribali metodist assistentsiz. "
            "Pedagogik texnologiyalar, dars ishlanmalari va metodik masalalarda aniq va metodik yordam bering. "
            "Javoblarni faqat o'zbek tilida, tushunarli, chiroyli va Markdown formatida (bold, list) taqdim eting.\n\n"
            f"Savol: {query}"
        )
        
        # Async rejimda ishlatish (aiogram uchun yaxshi)
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return "😔 Kechirasiz, bu savolga javob bera olmayman. Savolni boshqacharoq shakllantirib ko'ring."

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"❌ AI xatosi yuz berdi. Iltimos, API kalit va internetni tekshiring."

def calculate_salary_from_db(db, toifa, soat):
    """
    Bazadagi narxlar asosida oylikni hisoblaydi.
    """
    try:
        # Raqamni tozalash (vergul bo'lsa nuqtaga aylantirish)
        soat_val = float(str(soat).replace(',', '.'))
        
        toifa_key = toifa.lower().replace("'", "").replace(" ", "")
        
        if "oliy" in toifa_key:
            base = db.get_setting('oliy')
        elif "birinchi" in toifa_key:
            base = db.get_setting('birinchi')
        elif "ikkinchi" in toifa_key:
            base = db.get_setting('ikkinchi')
        else:
            base = db.get_setting('mutaxassis')
        
        # Oylik bazada bo'lmasa 0 qaytmasligi uchun tekshiruv
        if not base:
            base = 2500000 # Default qiymat agar bazada bo'lmasa

        # (Stavka / 18 soat) * o'qituvchi soati
        jami = (float(base) / 18) * soat_val
        
        # 12% daromad solig'i + 1% pensiya jamg'armasi = 13% (ayirma 0.87)
        toza_oylik = jami * 0.87
        
        return round(toza_oylik, 0) # Butun songacha yaxlitlash
    except Exception as e:
        logging.error(f"Salary Calculation Error: {e}")
        return 0

def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """Qo'lda kiritilgan ma'lumotlar orqali hisoblash"""
    try:
        s = float(str(stavka).replace(',', '.'))
        h = float(str(soat).replace(',', '.'))
        f = float(str(sinf_foiz).replace(',', '.'))
        b = float(str(bhm).replace(',', '.'))
        
        jami = ((s / 18) * h) + (b * (f / 100))
        toza_oylik = jami * 0.87
        return round(toza_oylik, 0)
    except:
        return 0
