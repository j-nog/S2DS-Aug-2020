#!/usr/bin/env python
# coding: utf-8

"""
from nationbetter.pdf_page_parsing import build_pdf_df

df_annot, df_content, df_data = build_pdf_df(file_names[1])
"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.layout import LAParams, LTTextContainer, LTTextLine, LTText, LTChar, LTTextBoxHorizontal, LTLine
from pdfminer.pdftypes import resolve1, PDFObjRef

from io import StringIO

import sys
import pandas as pd

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
