import google.generativeai as genai
from config import GEMINI_API_KEY

# Gemini API ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

async def get_ai_help(query):
    """Google Gemini orqali metodik yordam olish"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Yangiroq va tezroq model
        
        prompt = (
            "Siz o'qituvchilarga yordam beruvchi aqlli assistentsiz. "
            "Javoblarni faqat o'zbek tilida va tushunarli bering.\n\n"
            f"Savol: {query}"
        )
        
        response = model.generate_content(prompt)
        return response.text if response.text else "😔 Javob topilmadi."
    except Exception as e:
        return f"❌ AI xatosi: {str(e)}"

def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """Oylik hisoblash formulasi"""
    try:
        # Ma'lumotlar kelmasa, 0 deb qabul qilamiz
        s = float(stavka) if stavka else 0
        h = float(soat) if soat else 0
        f = float(sinf_foiz) if sinf_foiz else 0
        b = float(bhm) if bhm else 0
        
        # Formula: ((Stavka / 18) * Soat) + (BHM * foiz)
        jami = ((s / 18) * h) + (b * (f / 100))
        
        # 13% soliqni ayirib tashlaymiz (Daromad solig'i + Pensiya jamg'armasi)
        toza_oylik = jami * 0.87
        return round(toza_oylik, 2)
    except:
        return 0
