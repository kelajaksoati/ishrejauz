from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

def generate_certificate_pdf(name, score, subject=""):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    # --- Shriftni sozlash ---
    font_bold = "Helvetica-Bold"
    font_normal = "Helvetica"
    
    font_path = "Arial.ttf" # Agar loyihangizda Arial bo'lsa kirillcha ham ishlaydi
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', font_path))
            font_bold = "CustomFont"
            font_normal = "CustomFont"
        except: pass

    # --- Dizayn (Soddalashtirilgan va Ultra) ---
    can.setStrokeColorRGB(0.1, 0.4, 0.8)
    can.rect(50, 50, width-100, height-100, stroke=1, fill=0)

    # Sarlavha
    can.setFont(font_bold, 40)
    can.drawCentredString(width/2, 650, "SERTIFIKAT")

    # Ism
    can.setFont(font_normal, 25)
    can.drawCentredString(width/2, 530, name.upper())

    # Matn
    can.setFont(font_normal, 18)
    can.drawCentredString(width/2, 480, f"{subject} fani bo'yicha")
    can.drawCentredString(width/2, 450, f"Onlayn attestatsiyadan o'tdi")

    # Natija
    can.setFont(font_bold, 22)
    can.drawCentredString(width/2, 380, f"Natija: {score}%")

    # Sana va muhr o'rni
    can.setFont(font_normal, 12)
    can.drawString(100, 200, "Sana: 2024-2025")
    can.drawRightString(width-100, 200, "IshReja_Uz Adminstratsiyasi")

    can.save()
    packet.seek(0)
    return packet
