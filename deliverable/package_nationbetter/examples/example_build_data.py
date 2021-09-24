#!/usr/bin/env python
# coding: utf-8
import os
import pandas as pd
import platform
import re
import nationbetter
import time

dirname = os.path.dirname(os.path.abspath(os.path.join(__file__,'..')))
#Reading data files.
pdf_urls=nationbetter.read_txt(os.path.join(dirname,'pdf_urls.txt'))
urls=nationbetter.read_txt(os.path.join(dirname,'urls.txt'))

#Creating a folder to store the data (does no overwrite)
#path = nationbetter.get_data_folder()
path = nationbetter.get_data_folder(os.path.abspath(\
        os.path.join(__file__,'..','..','..')))
path = os.path.join(path,'data_nationbetter')
#Download the pdfs into raw_pdf folder
start = time.time()
#Extracting line for line text pdf (pdfminer)
for url in pdf_urls:
    nationbetter.get_lines_and_info(url,path)
print('Import finished at:')
print('\n -----------{}------------\n'.format(time.time()-start))

#Download & extract raw HTML data
for url in urls:
    nationbetter.scrape_govuk_guidance(url,path)

#For each extracted dict build formatted dataframe
start = time.time()
stored_pdf = os.listdir(os.path.join(path,'raw_pdf_dicts'))[1:]
for name in stored_pdf:
    name = os.path.join(path,'raw_pdf_dicts',name)
    nationbetter.pdf_dict_to_outputformat(name,path)
print('Transform finished at:')
print('\n -----------{}------------\n'.format(time.time()-start))

stored_html = os.listdir(os.path.join(path,'raw_html_dicts'))[1:]
for name in stored_html:
    name = os.path.join(path,'raw_html_dicts',name)
    nationbetter.build_segments_df(name,path)

pdf_folder = os.path.join(path,'formatted_pdf_dfs')
html_dict_folder = os.path.join(path,'raw_html_dicts')
html_folder = os.path.join(path,'formatted_html_dfs')
nationbetter.get_tagged_corpus(pdf_folder, html_folder,html_dict_folder, path) 
# # perform page analysis, disabeled in current version
# df_annot, df_content, df_data = pdf_page_parsing.build_pdf_df(file_name[1])
