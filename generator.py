from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def generate_certificate_pdf(name, score):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    # Dizayn qismi
    can.setFont("Helvetica-Bold", 30)
    can.drawCentredString(297, 600, "SERTIFIKAT")
    can.setFont("Helvetica", 20)
    can.drawCentredString(297, 500, f"{name}")
    can.drawCentredString(297, 450, f"Ball: {score}")
    can.save()
    packet.seek(0)
    return packet
