
"""
Functions for creating and restructuring dicts from pdf files for
backwards engineering the layout structure from the pdfminer.six layout
object (LTTextBox etc. see tree in:
https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html
"""
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTChar, LTTextBoxHorizontal


#set maxpage to number to only parse part of file for debugging
def get_lines_and_info(filename,maxpage=False):
    """
    Function that takes a pdf file and runs it trough pdfminer.six to parse the
    LTTextBox objects of the LAParams class returning a dict 
    containing the page numbers, box numbers, box position, line numbers, font
    size of current and previous line in the text. 
    """
    file = open(filename,'rb')
    columns = [
            'page_no',
            'box_no',
            'box_pos',
            'line_no',
            'line_pos',
            'previous_linefontsize',
            'curr_linefontsize',
            'text'
    ]

    data = {key : [] for key in columns}
    fontsize = None #Set fontsize to none for previous_linefontsize on 1st entry
    pagenumber = 0

    # parse over all textboxes and lines contained in them
    for page_layout in extract_pages(file):
        pagenumber += 1
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                lineno=0
                for text_line in element:
                    lineno += 1
                    #output line data
                    data['page_no'].append(pagenumber)
                    data['box_no'].append(element.index)
                    data['box_pos'].append(element.bbox)
                    data['line_no'].append(lineno)
                    data['previous_linefontsize'].append(fontsize)
                    data['line_pos'].append(text_line.bbox)
                    data['text'].append(text_line.get_text())
                    if not text_line.get_text().isspace():
                        #Recording fontsize of first nonspace character in line
                        for character in text_line:
                            if isinstance(character,LTChar):
                                if character.get_text().isspace() :
                                    continue
                                else:
                                    fontsize = character.size
                                    data['curr_linefontsize'].append(fontsize)
                                    break
                    else:
                        data['curr_linefontsize'].append(None)
        if pagenumber>maxpage and maxpage != False:
            break
    return data 

