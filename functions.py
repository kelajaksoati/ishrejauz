import logging
from google import genai
from config import AI_API_KEY

# Gemini AI yangi kutubxona mijozi
client = genai.Client(api_key=AI_API_KEY)

async def get_ai_answer(query):
    """
    Google Gemini 2.0 Flash orqali metodik yordam olish.
    404 xatoligi va eskirgan kutubxona muammolari hal qilingan.
    """
    try:
        prompt = (
            "Siz o'zbekistonlik o'qituvchilarga yordam beruvchi tajribali metodist assistentsiz. "
            "Pedagogik texnologiyalar, dars ishlanmalari va metodik masalalarda aniq yordam bering. "
            "Javoblarni faqat o'zbek tilida, tushunarli, chiroyli va Markdown formatida taqdim eting.\n\n"
            f"Savol: {query}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        if response and response.text:
            return response.text
        return "😔 Javob topilmadi. Savolni boshqacharoq shaklda berib ko'ring."
        
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "❌ AI xizmatida vaqtinchalik uzilish yuz berdi. Iltimos, keyinroq urinib ko'ring."

def calculate_salary_advanced(db, data):
    """
    O'qituvchi oyligini barcha ustamalar bilan hisoblash:
    - Sinf rahbarlik
    - Daftar tekshirish
    - Sertifikat (% da)
    - Ish staji
    - Olis hudud
    - 13% soliq chegirmasi
    """
    try:
        # Bazadan joriy sozlamalarni olish
        settings = db.get_settings()
        
        # Kiruvchi ma'lumotlarni tozalash
        soat = float(str(data.get('soat', 0)).replace(',', '.'))
        bhm = settings.get('bhm', 375000)
        toifa = str(data.get('toifa', 'mutaxassis')).lower()
        
        # 1. Toifa bo'yicha bazaviy stavka (bazadan yoki standart qiymat)
        stavka = settings.get(toifa, 3500000)
        
        # Mantiqiy tekshiruv: Agar bazada koeffitsient bo'lsa (masalan 11.64)
        if stavka < 100:
            stavka = bhm * stavka
            
        # Asosiy dars soati uchun hisoblangan maosh
        maosh = (stavka / 18) * soat

        # 2. Sinf rahbarlik (BHMning 50% miqdorida)
        if data.get('sinf_rahbar'):
            maosh += bhm * 0.5

        # 3. Daftar tekshirish (BHMning 15% miqdorida)
        if data.get('daftar_tekshirish'):
            maosh += bhm * 0.15

        # 4. Sertifikat ustamasi (Stavkaga nisbatan foizda, masalan 20 yoki 50)
        sertifikat_foiz = int(data.get('sertifikat', 0))
        if sertifikat_foiz > 0:
            maosh += stavka * (sertifikat_foiz / 100)

        # 5. Ish staji (Ko'p yillik xizmati uchun)
        staj = int(data.get('staj', 0))
        if staj >= 25:
            maosh += stavka * 0.20  # 20% ustama
        elif staj >= 10:
            maosh += stavka * 0.10  # 10% ustama

        # 6. Olis hudud (Odatda stavkaning 25% miqdorida)
        if data.get('olis_hudud'):
            maosh += stavka * 0.25

        # 7. Soliqlar (12% daromad + 1% INPS = 13% chegirma)
        # Qo'lga tegadigan summa = Jami * 0.87
        net_salary = maosh * 0.87
        
        return round(net_salary, 0)
        
    except Exception as e:
        logging.error(f"Salary Calculation Error: {e}")
        return 0
