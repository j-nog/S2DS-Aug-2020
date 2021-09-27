#!/usr/bin/env python
#!/usr/bin/env python
# coding: utf-8
"""
from pdf_scraping import *

create_folder('input')
pdf_links["www.1", "www.2", "www.3"]
file_names = download_pdfs(pdf_links)

dict_layout = get_lines_and_info(file_names[1])
df_layout = pd.DataFrame(dict_layout)

df_annot, df_content, df_data = build_pdf_df(file_names[1])
"""

from pdfminer.high_level import extract_pages
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.layout import LAParams, LTTextContainer, LTTextLine, LTText, LTChar, LTTextBoxHorizontal, LTLine
from pdfminer.pdftypes import resolve1, PDFObjRef

from io import StringIO

import os
import sys
import requests
import pandas as pd

#set maxpage to number to only parse part of file for debugging
def get_lines_and_info(filename,maxpage=False):
    """
    Functions for creating and restructuring dicts from pdf files for
    backwards engineering the layout structure from the pdfminer.six layout
    object (LTTextBox etc. see tree in:
    https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html
    
    Function that takes a pdf file and runs it trough pdfminer.six to parse the
    LTTextBox objects of the LAParams class returning a dict 
    containing the page numbers, box numbers, box position, line numbers, font
    size of current and previous line in the text. 
    """
    file = open(filename,'rb')
    columns = ['page_no', 'box_no', 'box_pos', 'line_no', 'line_pos', 
               'previous_linefontsize', 'curr_linefontsize', 'text']

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

def create_folder(input_path="input"):
    """
    Create a data folder, if it does not exist, and name it as input
    """
    current_path = os.getcwd()
    if not os.path.exists(input_path):
        os.makedirs(input_path)    

def download_pdfs(url_links):
    """
    Function to download pdf files from the given links
    Returns list of PDF [file_names]
    
    TODO : Get time while downloading files, for later use as a timestamp (as @Bernhard did)
    """    
    input_path = 'input'
    create_folder(input_path)
    os.chdir(input_path)
    file_names = []
    for url_link in url_links:
        file_name = url_link.split('/')[-1]
        file_names.append(file_name)
        if not os.path.exists(file_name):
            r = requests.get(url_link, allow_redirects=True)
            open(file_name, 'wb').write(r.content)
    os.chdir('..')
    return file_names

def parse_table_of_contents(layout):
    """
    With an open Layout object, parse the table of contents 
    Returns list contents of the document, data structure 
    [content_title, goto_page, [content_obj_bbox]]    
    """
    contents = []
    content_title = None
    goto_page = None
    
    for obj in layout:        
        if isinstance(obj, LTTextBoxHorizontal):
            obj_str = obj.get_text().strip()              
            """
            FIXME : page-wise reading, exit from document when first content is found
            e.g.
            if "PART A – HEALTH AND CARE VISA" in obj_str.split("\n")[0]:
                break
            """
            find_str = ".."              # TODO : check if it always works ?
            if find_str in obj_str:      # heuristically
                if len(obj_str) < 100:   # heuristically / experimentally
                    obj_strs = obj_str.split(find_str)
                    content_title = obj_strs[0]
                    goto_page = int(obj_strs[-1].replace('\n','').replace('.',''))
                    contents.append((content_title, goto_page, obj.bbox))
                else:
                    obj_strs = [t.split("\n") for t in list(filter(str.strip, obj_str.split('..')))]
                    for i,obj_str in enumerate(obj_strs):
                        if i==0:
                            content_title = obj_str[0]
                            goto_page = int(obj_strs[1][0].split(".")[-1])
                        elif i == len(obj_strs)-1:
                            content_title = obj_str
                            goto_page = obj_strs[i][0]
                            break
                        else:
                            content_title = " ".join([t for i,t in enumerate(obj_str) if i != 0])
                            goto_page = int(obj_strs[i+1][0].split(".")[-1])
                        contents.append((content_title, goto_page, obj.bbox))
    return contents

def parse_annotations(page):
    """
    With an open PDFPage object, get the annot attribute
    Return list of annotations
    [objectID, positions, urls, {annotationDict}]    
    """
    annotations = []
    destID = None
    position = None
    url = None
    annotationDict = None
    
    for annot in resolve1(page.annots):
        if isinstance(annot, PDFObjRef):
            annotationDict = annot.resolve()
            # Skip over any annotations that are not links
            if str(annotationDict["Subtype"]) != "/'Link'":
                continue
            destID = 0
            position = annotationDict["Rect"]
            uriDict = "None"
            if any(k in annotationDict for k in {"Dest", "D"}):                
                destID = (annotationDict["Dest"][0]).objid                
                url = "Cross reference"
            elif "A" in annotationDict:
                # Key A contains PDFObjRef, then resolve it again
                if isinstance(annotationDict["A"], PDFObjRef):
                    uriDict = resolve1(annotationDict["A"])
                    if any(k in uriDict for k in {"Dest", "D"}): 
                        destID = (uriDict["D"][0]).objid
                else:
                    uriDict = annotationDict["A"]
                # Check if the key exists within resolved uriDict
                if str(uriDict["S"]) == "/'GoTo'":
                    url = "Cross reference"
                elif str(uriDict["S"]) == "/'URI'":
                    url = str(uriDict["URI"])
                    url = url.lstrip("b")
                    url = url.replace("'", "")
                else:
                    url = "None"
                    # Skip if key S in uriDict does not contain value URI, GoTo
                    continue
            else:
                sys.stderr.write("Warning: unknown key in annotationDict : ", annotationDict)
            annotations.append((destID, position, url, annotationDict))
        else:
            sys.stderr.write("Warning: unknown annotation: %s\n" % annot)            
    return annotations

def scrape_pdf(doc, file_name):
    """
    With an open PDFDocument object, loop over each page and layout
    Returns
    contents  [file_name, page_number, content_title, goto_page, [content_obj_bbox]]  
    data  [file_name, page_number, page_raw_text, [cross_refs], [positions], [urls], {annotations}]
    """
    manager = PDFResourceManager()
    output = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    converter = TextConverter(manager, output, codec=codec, laparams=laparams)
    device = PDFPageAggregator(manager, laparams=laparams)
    interpreter = PDFPageInterpreter(manager, device)
    page_interpreter = PDFPageInterpreter(manager, converter)
       
    content_cols = ["file_name", "page_number", "content_title", "goto_page", "obj_bbox"]
    content_dict = {key : [] for key in content_cols}
    
    annot_cols = ["file_name", "page_number", "destID", "position", "url", "annotationDict"]
    annot_dict = {key : [] for key in annot_cols}

    data_cols = ["file_name", "page_number", "raw_text"]
    data_dict = {key : [] for key in data_cols}
    
    page_no = 0
    for page_number, page in enumerate(PDFPage.create_pages(doc)):
        if page_number == page_no:
            page_interpreter.process_page(page)
            raw_text = output.getvalue()
            output.truncate(0)
            output.seek(0)
        
        page_no += 1
        
        interpreter.process_page(page)
        layout = device.get_result()

        # Storing the information for each page
        if page.annots:
            annotations = parse_annotations(page)
            for k in annotations:
                annot_dict["file_name"].append(file_name)                
                annot_dict["page_number"].append(page_no)                
                annot_dict["destID"].append(k[0])                
                annot_dict["position"].append(k[1])
                annot_dict["url"].append(k[2])
                annot_dict["annotationDict"].append(k[3])
            
            contents = parse_table_of_contents(layout)
            for k in contents:
                content_dict["file_name"].append(file_name)                
                content_dict["page_number"].append(page_no)                
                content_dict["content_title"].append(k[0])                
                content_dict["goto_page"].append(k[1])
                content_dict["obj_bbox"].append(k[2])

        data_dict["file_name"].append(file_name)
        data_dict["page_number"].append(page_no)
        data_dict["raw_text"].append(raw_text)   

    converter.close()
    output.close()
    device.close()        
    return annot_dict, content_dict, data_dict

def build_pdf_df(file_name):
    """
    Returns 3 df for a pdf containing annots, contents, data
    """    
    fp = open(file_name, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    print('\n\n\tProcessing file         ', file_name)
    annot_dict, content_dict, data_dict = scrape_pdf(document, file_name)
    df_annot = pd.DataFrame(annot_dict)
    df_content = pd.DataFrame(content_dict)
    df_data = pd.DataFrame(data_dict)
    return df_annot, df_content, df_data
