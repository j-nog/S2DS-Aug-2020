from PyPDF2 import PdfFileWriter, PdfFileReader

inputpdf = PdfFileReader(open("Tier-2-5-sponsor-guidance_Jul-2020_v1.0.pdf", "rb"))

out_len = 10
output = PdfFileWriter()
for i in range(10):
    output.addPage(inputpdf.getPage(i))
with open("document-page%s.pdf" % i, "wb") as outputStream:
    output.write(outputStream)
