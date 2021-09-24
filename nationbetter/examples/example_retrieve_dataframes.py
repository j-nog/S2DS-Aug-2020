#!/user/bin/env python
# coding: utf-8
import os
import nationbetter
import pandas as pd

#path = nationbetter.get_data_folder()
path = nationbetter.get_data_folder(os.path.abspath(\
        os.path.join(__file__,'..','..','..','..')))
path = os.path.join(path,'nationbetter_data')

# listing the possible imports 
pdf_names = os.listdir(os.path.join(path,'formatted_pdf_dfs'))[1:]
html_names = os.listdir(os.path.join(path,'formatted_html_dfs'))[1:]
print('To access one of the files in formatted_pdf_dfs and formatted_html_dfs,\
        select the wanted name from\n {0}\n {1}\n using indexing'\
        .format(pdf_names,html_names))
# Importing the datafame to variable
some_pdf_df = nationbetter.import_source_to_df(os.path.join(path,\
        'formatted_pdf_dfs/',pdf_names[2]))
some_html_df = nationbetter.import_source_to_df(os.path.join(path,\
        'formatted_html_dfs/',html_names[2]))
print('Now the dict is in some_html_dict, see?:\n {}'\
        .format(some_html_df.head()))
