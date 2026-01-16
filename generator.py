from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

def generate_certificate_pdf(name, score, subject="Pedagogika"):
    """
    O'qituvchilar uchun professional sertifikat yaratish funksiyasi.
    name: Foydalanuvchi ismi
    score: Test natijasi (foizda)
    subject: Fan nomi (default: Pedagogika)
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    width, height = A4 # A4 o'lchami: 595.27 x 841.89

    # --- 1. Shriftlarni sozlash (Kirill va Lotin yozuvi uchun) ---
    font_bold = "Helvetica-Bold"
    font_normal = "Helvetica"
    
    # Loyihada Arial.ttf bo'lsa, o'zbekcha harflar (o', g', sh, ch) xatosiz chiqadi
    font_path = "Arial.ttf" 
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', font_path))
            font_bold = "CustomFont"
            font_normal = "CustomFont"
        except:
            pass

    # --- 2. Vizual Dizayn (Ramka va fon) ---
    # Ko'k rangli chiroyli ramka chizish
    can.setStrokeColorRGB(0.1, 0.4, 0.8) # To'q ko'k rang
    can.setLineWidth(3)
    can.rect(40, 40, width-80, height-80, stroke=1, fill=0) # Tashqi qalin ramka
    
    can.setLineWidth(1)
    can.rect(50, 50, width-100, height-100, stroke=1, fill=0) # Ichki ingichka ramka

    # --- 3. Matnlarni joylashtirish ---
    
    # Sarlavha
    can.setFont(font_bold, 45)
    can.setFillColorRGB(0.1, 0.3, 0.6)
    can.drawCentredString(width/2, 680, "SERTIFIKAT")

    # "Ushbu sertifikat berildi:" matni
    can.setFont(font_normal, 18)
    can.setFillColorRGB(0, 0, 0)
    can.drawCentredString(width/2, 600, "Ushbu hujjat egasi")

    # Foydalanuvchi ismi (Katta harflarda va qalin)
    can.setFont(font_bold, 28)
    can.drawCentredString(width/2, 550, name.upper())

    # Asosiy matn
    can.setFont(font_normal, 20)
    can.drawCentredString(width/2, 490, f"{subject} fani bo'yicha")
    can.drawCentredString(width/2, 460, "o'tkazilgan onlayn attestatsiya testida")
    can.drawCentredString(width/2, 430, "muvaffaqiyatli ishtirok etib, quyidagi")
    can.drawCentredString(width/2, 400, "natijani qayd etdi:")

    # Natija (Foizda)
    can.setFont(font_bold, 35)
    can.setFillColorRGB(0.1, 0.5, 0.1) # Yashil rang (muvaffaqiyat ramzi)
    can.drawCentredString(width/2, 330, f"{score}%")

    # --- 4. Pastki qism (Sana va Tasdiq) ---
    can.setFont(font_normal, 12)
    can.setFillColorRGB(0, 0, 0)
    
    # Sana (Hozirgi yilni dinamik qo'yish ham mumkin)
    can.drawString(80, 150, "Sana: 2024-2025 o'quv yili")
    
    # Sayt yoki bot nomi
    can.drawRightString(width-80, 150, "IshReja_Uz Telegram Bot")
    
    # QR-kod yoki Muhr o'rni uchun dekorativ doira
    can.setStrokeColorRGB(0.8, 0.8, 0.8)
    can.circle(width/2, 150, 40, stroke=1, fill=0)
    can.setFont(font_normal, 8)
    can.drawCentredString(width/2, 148, "MUHR O'RNI")

    # Yakunlash
    can.showPage()
    can.save()
    packet.seek(0)
    return packet
