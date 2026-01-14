import logging
import google.generativeai as genai
from config import AI_API_KEY  # Config faylingizdagi nomga qarab tekshiring

# AI (Gemini) Sozlamasi
genai.configure(api_key=AI_API_KEY)

async def get_ai_answer(query):
    """
    Google Gemini (1.5-flash) orqali metodik yordam olish.
    Xavfsizlik sozlamalari javob to'xtab qolmasligini ta'minlaydi.
    """
    try:
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
            "Pedagogik texnologiyalar, dars ishlanmalari va metodik masalalarda aniq yordam bering. "
            "Javoblarni faqat o'zbek tilida, tushunarli va Markdown formatida taqdim eting.\n\n"
            f"Savol: {query}"
        )
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return "😔 Kechirasiz, bu savolga javob topa olmadim. Savolni boshqacharoq yozib ko'ring."

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "❌ AI xatosi yuz berdi. Iltimos, keyinroq urinib ko'ring."

def calculate_salary_from_db(db, toifa, soat):
    """
    Bazadan BHM va toifa koeffitsientlarini olib oylikni hisoblash.
    Soliqlar (13%) chegirilgan holda 'qo'lga tegadigan' summani qaytaradi.
    """
    try:
        # Bazadan barcha sozlamalarni olish
        settings = db.get_settings() 
        
        # BHM qiymatini olish (default 375,000 so'm)
        bhm = settings.get('bhm', 375000)
        
        # Kiruvchi soatni raqamga o'tkazish
        soat_val = float(str(soat).replace(',', '.'))
        
        # Toifaga qarab koeffitsient kalitini aniqlash
        toifa_name = toifa.lower()
        if "oliy" in toifa_name:
            coeff_key = 'oliy'
        elif "birinchi" in toifa_name:
            coeff_key = 'birinchi'
        elif "ikkinchi" in toifa_name:
            coeff_key = 'ikkinchi'
        else:
            coeff_key = 'mutaxassis'

        # Bazadan koeffitsientni olish (default 1.0)
        coeff = settings.get(coeff_key, 1.0)
        
        # 1. Jami hisoblangan (Yalpi) maosh
        # Formula: (BHM * Koeffitsient) * (Soat / 18)
        gross_salary = (float(bhm) * float(coeff)) * (soat_val / 18)
        
        # 2. Soliqlarni ayirish (12% Daromad + 1% INPS = 13%)
        # Qo'lga tegadigan summa = Yalpi maosh * 0.87
        net_salary = gross_salary * 0.87
        
        return round(net_salary, 0)
        
    except Exception as e:
        logging.error(f"Oylik hisoblashda xato: {e}")
        return 0
