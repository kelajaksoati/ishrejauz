import logging
import os
from google import genai
from config import AI_API_KEY
from fpdf import FPDF

# Gemini AI mijozi (Yangi google-genai kutubxonasi uchun)
client = genai.Client(api_key=AI_API_KEY)

# --- AI FUNKSIYASI ---
async def get_ai_answer(query):
    """Google Gemini orqali metodik yordam olish."""
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
        return "❌ AI xizmatida vaqtinchalik uzilish yuz berdi."

# --- OYLIK HISOBLASH FUNKSIYASI ---
def calculate_salary_final(data, db):
    """O'qituvchi oyligini barcha ustamalar bilan hisoblash va matn qaytarish."""
    try:
        settings = db.get_settings()
        
        # Asosiy ma'lumotlarni olish
        soat = float(str(data.get('soat', 0)).replace(',', '.'))
        bhm = int(settings.get('bhm', 375000))
        toifa = str(data.get('toifa', 'mutaxassis')).lower()
        
        # Toifa stavkasini aniqlash (bazadan)
        toifa_key = {
            'oliy': 'oliy', 'birinchi': 'birinchi', 
            'ikkinchi': 'ikkinchi', 'mutaxassis': 'mutaxassis'
        }.get(toifa, 'mutaxassis')
        
        stavka = int(settings.get(toifa_key, 3500000))
        
        # 1. Asosiy dars soati uchun maosh (18 soat = 1 stavka)
        asosiy_maosh = (stavka / 18) * soat
        
        # 2. Ustamalar (Admin panelda belgilangan summalardan olinadi)
        sinf_rahbar_summa = 0
        if data.get('sinf_rahbar'):
            sinf_rahbar_summa = bhm * 0.5  # Odatda BHMning 50%
            
        daftar_summa = 0
        if data.get('daftar'):
            # Bazada 'daftar' narxi bo'lsa shuni oladi, bo'lmasa 15% hisoblaydi
            daftar_ustama = int(settings.get('daftar', 0))
            daftar_summa = daftar_ustama if daftar_ustama > 0 else (bhm * 0.15)
            
        kabinet_summa = 0
        if data.get('kabinet'):
            kabinet_summa = int(settings.get('kabinet', 0)) if int(settings.get('kabinet', 0)) > 0 else (bhm * 0.5)

        # 3. Sertifikat ustamasi (Stavkaga nisbatan foizda)
        sert_summa = 0
        if data.get('sertifikat'):
            # Agar foydalanuvchi "Ha" degan bo'lsa, standart 20% yoki 50% ni kodingizda so'rash kerak
            # Hozircha namunaviy 20%
            sert_summa = stavka * 0.20 

        # 4. Olis hudud (25%)
        olis_summa = 0
        if data.get('olis_hudud'):
            olis_summa = stavka * 0.25

        # JAMI hisoblash
        total_gross = asosiy_maosh + sinf_rahbar_summa + daftar_summa + kabinet_summa + sert_summa + olis_summa
        
        # Daromad solig'i (12%) va Pensiya (1%) = Jami 13% ushlanma
        soliq = total_gross * 0.13
        final_salary = total_gross - soliq

        # Natijani chiroyli ko'rinishda shakllantirish
        res = (
            f"📊 **Oylik ish haqi hisob-kitobi:**\n\n"
            f"🔹 **Toifa stavkasi:** {stavka:,.0f} so'm\n"
            f"🔹 **Dars soati:** {soat} soat\n"
            f"--- Ustamalar ---\n"
            f"➕ **Dars maoshi:** {asosiy_maosh:,.0f} so'm\n"
        )
        if sinf_rahbar_summa: res += f"➕ **Sinf rahbarlik:** {sinf_rahbar_summa:,.0f} so'm\n"
        if daftar_summa: res += f"➕ **Daftar tekshirish:** {daftar_summa:,.0f} so'm\n"
        if kabinet_summa: res += f"➕ **Kabinet mudirligi:** {kabinet_summa:,.0f} so'm\n"
        if sert_summa: res += f"➕ **Sertifikat (AI):** {sert_summa:,.0f} so'm\n"
        if olis_summa: res += f"➕ **Olis hudud:** {olis_summa:,.0f} so'm\n"
        
        res += (
            f"\n💰 **Jami (Gryutto):** {total_gross:,.0f} so'm\n"
            f"✂️ **Soliq va ushlanmalar (13%):** {soliq:,.0f} so'm\n"
            f"✅ **Qo'lga tegadigan summa (Netto):** {round(final_salary, 0):,.0f} so'm"
        ).replace(',', ' ')
        
        return res
        
    except Exception as e:
        logging.error(f"Salary Calculation Error: {e}")
        return "❌ Hisoblashda xatolik yuz berdi. Ma'lumotlar to'g'riligini tekshiring."

# --- PDF GENERATOR --- (O'zgarishsiz qoldi, faqat shrift muammosi uchun izoh)
def generate_salary_pdf(data, total_salary, user_name):
    # PDF generatsiya kodi... (Yuqoridagi kodingiz kabi)
    pass
