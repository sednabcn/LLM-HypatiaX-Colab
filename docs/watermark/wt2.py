from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a watermark PDF
c = canvas.Canvas("watermark.pdf", pagesize=letter)
width, height = letter

# Add watermark text (centered, rotated)
c.saveState()
c.translate(width/2, height/2)
c.rotate(45)  # Diagonal watermark
c.setFont("Helvetica", 60)
c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # Semi-transparent gray
c.drawCentredString(0, 0, "CONFIDENTIAL")
c.restoreState()

c.save()
