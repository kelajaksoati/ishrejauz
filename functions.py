import openai
from config import OPENAI_API_KEY

# OpenAI API kalitini sozlash
openai.api_key = OPENAI_API_KEY

def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """
    O'qituvchi oyligini hisoblash mantiqi:
    1. Dars soati uchun pul (stavka / 18 soat * amaldagi soat)
    2. Sinf rahbarlik uchun qo'shimcha (BHMning foizi)
    3. Soliqlar (13% ayiriladi)
    """
    dars_puli = (stavka / 18) * soat
    sinf_puli = bhm * (sinf_foiz / 100)
    
    jami = dars_puli + sinf_puli
    toza_oylik = jami * 0.87  # 12% daromad solig'i + 1% INPS = 13% ayirma
    
    return round(toza_oylik, 2)

async def get_ai_help(query):
    """
    OpenAI orqali o'qituvchiga metodik yordam berish funksiyasi.
    """
    try:
        # Haqiqiy API so'rovi
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {
                    "role": "system", 
                    "content": "Siz o'qituvchilarga dars ishlanmasi, insho va metodik yordam beruvchi aqlli yordamchisiz. Javoblarni faqat o'zbek tilida bering."
                },
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        # Agar API kalitda pul tugasa yoki xato bo'lsa, foydalanuvchiga tushunarli javob qaytaradi
        return f"❌ AI bilan bog'lanishda xato yuz berdi. Iltimos, keyinroq urinib ko'ring yoki admin bilan bog'laning.\n\nXato matni: {str(e)}"
