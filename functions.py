import logging
import google.generativeai as genai
from config import AI_API_KEY

# Gemini AI sozlamasi
genai.configure(api_key=AI_API_KEY)

async def get_ai_answer(query):
    """
    Google Gemini (1.5-flash) orqali o'qituvchilarga metodik yordam berish.
    Xavfsizlik sozlamalari blokirovkasiz ishlashni ta'minlaydi.
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
            "Javoblarni faqat o'zbek tilida, tushunarli, chiroyli va Markdown formatida taqdim eting.\n\n"
            f"Savol: {query}"
        )
        
        response = model.generate_content(prompt)
        return response.text if response and response.text else "😔 Javob topilmadi."
        
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "❌ AI bilan bog'lanishda xato yuz berdi. Iltimos, keyinroq urinib ko'ring."

def calculate_salary_from_db(db, toifa, soat):
    """
    Bazadagi stavkalar yoki koeffitsientlar asosida oylikni hisoblaydi.
    13% soliq (12% daromad + 1% pensiya) avtomatik chegiriladi.
    """
    try:
        # Bazadan barcha sozlamalarni lug'at ko'rinishida olamiz
        settings = db.get_settings()
        
        # Kiruvchi soatni formatlash (nuqta yoki vergul bo'lsa ham)
        soat_val = float(str(soat).replace(',', '.'))
        toifa_name = toifa.lower()
        
        # BHM qiymati (agar koeffitsient ishlatilsa kerak bo'ladi)
        bhm = settings.get('bhm', 375000)
        
        # Toifa kalitini aniqlash va bazadagi qiymatni olish
        if "oliy" in toifa_name:
            val = settings.get('oliy', 5000000)
        elif "birinchi" in toifa_name:
            val = settings.get('birinchi', 4500000)
        elif "ikkinchi" in toifa_name:
            val = settings.get('ikkinchi', 4000000)
        else:
            val = settings.get('mutaxassis', 3500000)

        # Mantiqiy tekshiruv: 
        # Agar bazadagi qiymat kichik bo'lsa (masalan 10 dan kichik), demak bu koeffitsient.
        # Agar katta bo'lsa (masalan 1 000 000 dan katta), demak bu tayyor stavka summasi.
        if val < 50: 
            stavka = bhm * val
        else:
            stavka = val

        # Hisoblash formulasi: (Stavka / 18 soat) * haqiqiy dars soati
        gross_salary = (stavka / 18) * soat_val
        
        # Qo'lga tegadigan summa: 13% soliq chegirilgan (100% - 13% = 87%)
        net_salary = gross_salary * 0.87
        
        return round(net_salary, 0)
        
    except Exception as e:
        logging.error(f"Calculation Error: {e}")
        return 0
