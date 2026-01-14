import google.generativeai as genai
from config import GEMINI_API_KEY # OpenAI kaliti o'rniga Gemini kaliti

# Gemini API sozlamalari
genai.configure(api_key=GEMINI_API_KEY)

def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """
    O'qituvchi oyligini hisoblash mantiqi (O'zgarishsiz qoldi):
    1. Dars soati uchun pul
    2. Sinf rahbarlik
    3. 13% soliqlar ayirmasi
    """
    # Stavka yoki BHM ma'lumotlar bazasidan None kelsa, xato bermasligi uchun
    stavka = float(stavka) if stavka else 0
    bhm = float(bhm) if bhm else 0
    
    dars_puli = (stavka / 18) * soat
    sinf_puli = bhm * (sinf_foiz / 100)
    
    jami = dars_puli + sinf_puli
    toza_oylik = jami * 0.87  # 13% ayirma
    
    return round(toza_oylik, 2)

async def get_ai_help(query):
    """
    Google Gemini orqali o'qituvchiga metodik yordam berish funksiyasi.
    """
    try:
        # Gemini modelini sozlash
        model = genai.GenerativeModel('gemini-pro')
        
        # Tizim ko'rsatmasi va foydalanuvchi so'rovi birlashtiriladi
        full_prompt = (
            "Siz o'qituvchilarga dars ishlanmasi, insho va metodik yordam beruvchi aqlli yordamchisiz. "
            "Javoblarni faqat o'zbek tilida, chiroyli va tushunarli tartibda bering.\n\n"
            f"Foydalanuvchi so'rovi: {query}"
        )
        
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "😔 AI javob qaytara olmadi. Iltimos, savolni boshqacharoq shakllantiring."
            
    except Exception as e:
        return f"❌ Gemini AI bilan bog'lanishda xato: {str(e)}"
