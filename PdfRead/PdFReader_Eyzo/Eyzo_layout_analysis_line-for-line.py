#written in python 3.6.9
#open the pdf file

from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTTextLine, LTText, LTChar, LTTextBoxHorizontal, LTLine
import pandas as pd

filename ='Tier-2-5-sponsor-guidance_25pg.pdf'
file = open(filename,'rb')
columns = ['page_no','box_no','box_pos','line_no','previous_linefontsize','curr_linefontsize','text']
data = {key : [] for key in columns}
fontsize = None #Set fontsize to none set previous_linefontsize on first entry
pagenumber = 0
# parse over all pages and return required info about contents
for page_layout in extract_pages(file):
    pagenumber += 1
    for element in page_layout:
        if isinstance(element, LTTextBoxHorizontal):
            #print('element no:{}'.format(element.index)) #.index gives the element number 
            #print('at page:{}'.format(pagenumber))
            #print('text:{}'.format(element.get_text()))
            #print('position:{0},{1},{2},{3}'.format(element.bbox[0],element.bbox[1],element.bbox[2],element.bbox[3])) #bbox on objects that contain coordinates prints box position x0, y0, x1, y1, which describe size and margin

            lineno=0
            # This prints the fontsize of the first character in the textbox.
            # Unfortunately this includes newlines tabs and spaces so they 
            # they need to be filtred out by hand.
            for text_line in element:
                lineno += 1
                data['page_no'].append(pagenumber)
                data['box_no'].append(element.index)
                data['box_pos'].append(element.bbox)
                data['line_no'].append(lineno)
                data['previous_linefontsize'].append(fontsize)
                data['text'].append(text_line.get_text())
                for character in text_line:
                    if isinstance(character,LTChar):
                        if character.get_text().isspace() :
                            fontsize = None
                            continue
                        else:
                            #print('fontsize {}'.format(character.size))
                            ##print('firstchar {}'.format(character))
                            fontsize = character.size
                            data['curr_linefontsize'].append(fontsize)
                            break
                    data['curr_linefontsize'].append(fontsize)
    if pagenumber > 12:
        break

#populate dataframe with Data
df = pd.DataFrame(data)
df.name = filename
print(df.head())
df.to_csv('layout_analysis_out.csv')
print('lenght of cols:{}\n pageno:{}\n box_no:{}\nline_no{}\nprev_fontsz:{}\ncurrl_fontsz:{}\ntext:{}'.format(*[len(data[key]) for key in columns]))
