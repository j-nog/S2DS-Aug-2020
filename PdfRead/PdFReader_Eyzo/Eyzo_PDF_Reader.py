# Written in Python 3.6.9
"""
Exploratory file for reading pdfs in python

Some comment on the most efficient reader:
https://medium.com/analytics-vidhya/efficient-pdfs-processing-with-python-abffd75b1af7
"""

# Pymupdf - Eyzo
# Pypdf2 - Joao

# PDFMINER - Ercan TODO WHAT IS SOURCE DID YOU WRITE THIS?
from urllib.request import urlopen # lib for importing urls
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter #libs for converting
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from functools import reduce
import re

# #setting remote path
# urllink = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/752360/vaf1a-visitandshorttermstay-11-18.pdf"
# url = urlopen(urllink)
# filename = urllink.split('/')[-1]
#
# #downloads file into path were PDF reader is located
# import requests
# r = requests.get(urllink, allow_redirects=True)
# open(filename, 'wb').write(r.content)

# setting path by hand
filename='Tier-2-5-sponsor-guidance_25pg.pdf'

def convert_pdf_to_txt(path, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(path, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    return text

text = convert_pdf_to_txt(filename)

"""
Following along
https://medium.com/analytics-vidhya/text-preprocessing-for-nlp-natural-language-processing-beginners-to-master-fd82dfecf95
for cleaning
"""

#set url to <URL> keyword
def clean_url(pdf_string):
    return re.sub(r'http\S+','<URL>',re.sub(r'www.\S+','<URL>',pdf_string))

def clean_non_alphanumeric(pdf_string):
    return re.sub('[^a-zA-Z0-9]',' ',pdf_string)

def find_fields(pdf_string):
    ddmmyyyy_regex = re.compile(r'[dD]\s*[dD]\s*[mM]\s*[mM]\s*[yY]\s*[yY]\s*[yY]\s*[yY]')
    return ddmmyyyy_regex.sub('<DDMMYYYY>',pdf_string)

def tokenize_space_sep_expr(pdf_string):
    out = ''
    glue_tiers_regex = re.compile(r'[tT][iI][eE][rR]\s*')
    out += glue_tiers_regex.sub('tier',pdf_string)
    return out
# def act_ref(pdf_string):

text_clean = find_fields(clean_non_alphanumeric(clean_url(text))).strip()

text_clean2 = reduce(lambda text, x: x(text), [clean_url,clean_non_alphanumeric,tokenize_space_sep_expr], x).strip()

print('{:.100s}'.format(text_clean))
# print('{:.100s}'.format(text_clean2))
name = filename+'cleaned.txt'
outwrite = open(name, 'w')
write.write(text_clean)
