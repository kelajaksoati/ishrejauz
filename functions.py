import logging
import os
from google import genai
from config import AI_API_KEY
from fpdf import FPDF

# Gemini AI mijozi
client = genai.Client(api_key=AI_API_KEY)

# --- AI FUNKSIYASI ---
async def get_ai_answer(query):
    """Google Gemini 2.0 Flash orqali metodik yordam olish."""
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

# --- OYLIK HISOBLASH FUNKSIYASI ---
def calculate_salary_advanced(db, data):
    """O'qituvchi oyligini barcha ustamalar bilan hisoblash (13% soliq chegirmasi bilan)."""
    try:
        settings = db.get_settings()
        
        soat = float(str(data.get('soat', 0)).replace(',', '.'))
        bhm = int(settings.get('bhm', 375000))
        toifa = str(data.get('toifa', 'mutaxassis')).lower()
        
        # Toifa stavkasi
        stavka = int(settings.get(toifa, 3500000))
        if stavka < 100: # Agar koeffitsient bo'lsa
            stavka = bhm * stavka
            
        # Asosiy dars maoshi
        maosh = (stavka / 18) * soat

        # Ustamalar
        if data.get('sinf_rahbar'): maosh += bhm * 0.5
        if data.get('daftar_tekshirish'): maosh += bhm * 0.15

        # Sertifikat
        sert_foiz = int(data.get('sertifikat', 0))
        if sert_foiz > 0: maosh += stavka * (sert_foiz / 100)

        # Ish staji
        staj = int(data.get('staj', 0))
        if staj >= 25: maosh += stavka * 0.20
        elif staj >= 10: maosh += stavka * 0.10

        # Olis hudud
        if data.get('olis_hudud'): maosh += stavka * 0.25

        # Net oylik (13% ushlanma: 12% daromad + 1% INPS)
        net_salary = maosh * 0.87
        return round(net_salary, 0)
        
    except Exception as e:
        logging.error(f"Salary Calculation Error: {e}")
        return 0

# --- PDF GENERATOR FUNKSIYASI ---
def generate_salary_pdf(data, total_salary, user_name):
    """Hisoblangan oylik haqida PDF hisobot yaratish."""
    try:
        # 'downloads' papkasi mavjudligini tekshirish
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        pdf = FPDF()
        pdf.add_page()
        
        # Sarlavha
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Oylik Ish Haqi Hisoboti", ln=True, align='C')
        pdf.ln(10)
        
        # Ma'lumotlar jadvali
        pdf.set_font("Arial", size=12)
        
        # O'zbekcha harflar PDF'da xato bermasligi uchun replace ishlatamiz
        # (Chunki standart FPDF Arial shrifti o' va g' ni qo'llamasligi mumkin)
        safe_user_name = user_name.encode('latin-1', 'ignore').decode('latin-1')
        
        details = [
            ("Foydalanuvchi:", safe_user_name),
            ("Toifa:", str(data.get('toifa')).capitalize()),
            ("Dars soati:", f"{data.get('soat')} soat"),
            ("Sinf rahbarlik:", "Ha" if data.get('sinf_rahbar') else "Yo'q"),
            ("Daftar tekshirish:", "Ha" if data.get('daftar_tekshirish') else "Yo'q"),
            ("Sertifikat ustamasi:", f"{data.get('sertifikat')}%"),
            ("Ish staji:", f"{data.get('staj')} yil"),
            ("Olis hudud:", "Ha" if data.get('olis_hudud') else "Yo'q"),
        ]
        
        for label, value in details:
            pdf.cell(90, 10, txt=label, border=1)
            pdf.cell(100, 10, txt=value, border=1, ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        
        # Yakuniy natija
        formatted_salary = f"{total_salary:,.0f} so'm".replace(',', ' ')
        pdf.cell(190, 10, txt=f"Qo'lga tegadigan summa: {formatted_salary}", ln=True, align='R')
        
        file_path = f"downloads/oylik_{user_name.replace(' ', '_')}.pdf"
        pdf.output(file_path)
        return file_path
        
    except Exception as e:
        logging.error(f"PDF Generation Error: {e}")
        return None
