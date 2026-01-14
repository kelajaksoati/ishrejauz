import google.generativeai as genai
from config import GEMINI_API_KEY

# Gemini API ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

async def get_ai_answer(query):
    """Google Gemini orqali metodik yordam olish"""
    try:
        # Yangiroq va tezroq model: gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = (
            "Siz o'qituvchilarga yordam beruvchi aqlli assistentsiz. "
            "Pedagogik texnologiyalar, dars ishlanmalari va metodik masalalarda yordam bering. "
            "Javoblarni faqat o'zbek tilida, tushunarli va chiroyli formatda bering.\n\n"
            f"Savol: {query}"
        )
        
        response = model.generate_content(prompt)
        return response.text if response.text else "😔 Kechirasiz, bu savolga javob topolmadim."
    except Exception as e:
        return f"❌ AI xatosi yuz berdi. Keyinroq urinib ko'ring."

def calculate_salary_from_db(db, toifa, soat):
    """
    Bazadagi narxlar (stavka) asosida oylikni hisoblaydi.
    1 stavka = 18 soat deb olingan.
    """
    try:
        # Toifa nomini tozalash (masalan: "O'rta maxsus" -> "mutaxassis")
        toifa_key = toifa.lower().replace("'", "").replace(" ", "")
        
        if "oliy" in toifa_key:
            base = db.get_setting('oliy')
        elif "birinchi" in toifa_key:
            base = db.get_setting('birinchi')
        elif "ikkinchi" in toifa_key:
            base = db.get_setting('ikkinchi')
        else:
            base = db.get_setting('mutaxassis')
        
        # Hisoblash: (Stavka miqdori / 18 soat) * o'qituvchi soati
        jami = (base / 18) * float(soat)
        
        # Daromad solig'i va pensiya (13%) ayirib tashlanganda (qolgan qismi 87%)
        toza_oylik = jami * 0.87
        
        return round(toza_oylik, 2)
    except Exception as e:
        print(f"Hisoblashda xato: {e}")
        return 0

def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """
    Qo'lda kiritilgan ma'lumotlar orqali sinf rahbarlik bilan birga hisoblash.
    """
    try:
        s = float(stavka) if stavka else 0
        h = float(soat) if soat else 0
        f = float(sinf_foiz) if sinf_foiz else 0
        b = float(bhm) if bhm else 0
        
        # Formula: (Dars soati oyligi) + (Sinf rahbarlik foizi BHMga nisbatan)
        jami = ((s / 18) * h) + (b * (f / 100))
        
        # Soliqlar ayirilgandagi summa
        toza_oylik = jami * 0.87
        return round(toza_oylik, 2)
    except:
        return 0
