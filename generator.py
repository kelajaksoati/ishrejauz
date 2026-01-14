from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

def generate_certificate_pdf(name, score):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    # --- Shriftni aniqlash ---
    # Agar Arial.ttf fayli bot papkasida bo'lsa, uni ishlatadi (Kirill/Lotin uchun)
    # Agar fayl bo'lmasa, Helvetica (faqat Lotin) ishlatadi
    font_path = "Arial.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', font_path))
            font_bold = "CustomFont"
            font_normal = "CustomFont"
        except:
            font_bold = "Helvetica-Bold"
            font_normal = "Helvetica"
    else:
        # Ikkinchi koddan olingan standart shriftlar
        font_bold = "Helvetica-Bold"
        font_normal = "Helvetica"

    # --- Dizayn qismi ---
    # Sarlavha (Birinchi koddagi 30 razmer)
    can.setFont(font_bold, 30)
    can.drawCentredString(297, 600, "SERTIFIKAT")
    
    # Ism (Lotin va Kirillni qo'llab-quvvatlovchi qism)
    can.setFont(font_normal, 20)
    can.drawCentredString(297, 500, f"{name}")
    
    # Ball (Ikkinchi kod mantiqi)
    can.setFont(font_normal, 18)
    can.drawCentredString(297, 450, f"Ball: {score}")
    
    can.save()
    packet.seek(0)
    return packet
