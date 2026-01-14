from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

def generate_tavsifnoma(name, school):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica-Bold", 20)
    can.drawString(200, 750, "TAVSIFNOMA")
    can.setFont("Helvetica", 14)
    text = f"Ushbu tavsifnoma {school} maktabi o'qituvchisi {name}ga berildi..."
    can.drawString(50, 700, text)
    can.save()
    packet.seek(0)
    return packet
