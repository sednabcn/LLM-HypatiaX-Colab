from pypdf import PdfReader, PdfWriter

# Load your watermark PDF
watermark = PdfReader("watermark.pdf").pages[0]

# Load the document you want to watermark
reader = PdfReader("document.pdf")
writer = PdfWriter()

# Apply watermark to all pages
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

# Save the watermarked PDF
with open("watermarked.pdf", "wb") as output:
    writer.write(output)
