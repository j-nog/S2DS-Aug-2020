#!/usr/bin/env python
# coding: utf-8
import os
import sys
import requests
import re
import csv
import json
import pickle
import pandas as pd

def read_txt(read_file):
    """
    Reads folders containing urls by seraching out strings containing
    'http' and deletes any other junk.
    """
    get_url = re.compile(r'http[^"<>#%{}|\^~`\,\s]*')
    strip_compare = re.compile(r'www.\S*$')
    f = open(read_file,'r')
    in_file = f.readlines() 
    https = [get_url.search(in_file[ntry]) for ntry in range(len(in_file))]
    https = list(filter(None,https))
    https = [https[ntry].group() for ntry in range(len(https))]
    f.close()
    return(list(filter(None,https)))

def get_data_folder(output_path):
    """
    Create a data folder for storing the data in ~/S2DS/NationBetter/data, 
    if it does not exist.
    """
    #output_path = "~/S2DS/NationBetter/data" 
    #output_path = os.path.expanduser(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)    
        print('Path for storing data created in:{}.'.format(output_path))
    return output_path 

def get_inner_folder(root,name):
    """
    Create subfolters for get_data_folder()
    """
    output_path = os.path.join(root,name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print('Path for storing {0}, created in, {1}.'.format(name,root))
    return output_path
    
def download_pdfs(url_link, input_path="input"):
    """
    Function to download pdf files from the given links
    Returns list of PDF [file_names]
    
    TODO : Get time while downloading files, for later use as a timestamp (as @Bernhard did)
    """   
    output_path = get_inner_folder(input_path,'raw_pdf')
    cdir = os.getcwd()
    os.chdir(output_path)
    file_name = url_link.split('/')[-1]
    file_name = os.path.join(output_path,file_name)
    if not os.path.exists(file_name):
        r = requests.get(url_link, allow_redirects=True)
        open(file_name, 'wb').write(r.content)
    os.chdir(cdir)
    print('Pdf files up to date and downloaded to {}.'.format(output_path))
    return file_name

def write_files(data,destenation_path,input_path,out_type='pickle'):
    """
    Method for storing dataframes and dicts to disk using different
    formats.
    """
    cdir = os.getcwd()
    #last_part = re.compile(r'[^/]*$') # FIXME \ split
    #get_in_name = last_part.search(input_path)
    #get_in_name = get_in_name.group()
    get_in_name = os.path.split(input_path)[1]
    rm_extention = re.compile(r'^[^.]*')
    file_name = rm_extention.search(get_in_name)
    file_name = file_name.group()
    os.chdir(destenation_path)
    if out_type == 'pickle':
        if isinstance(data,pd.DataFrame):
            data.to_pickle(file_name+'.pkl')
        else:
            file_name+='.pkl'
            with open(file_name,'wb') as f:
                pickle.dump(data,f,pickle.HIGHEST_PROTOCOL)
    if out_type == 'json':
        if isinstance(data,pd.DataFrame):
            data.to_json(file_name+'.json',index=True)
        else:
            file_name+='.json'
            with open(file_name,'w') as f:
                json.dump(data,f)
    if out_type == 'csv':
        if isinstance(data,pd.DataFrame):
            data.to_csv(file_name+'.csv',index=True)
        else:
            file_name+='.csv'
            with open(file_name,'w') as f:
                csv_columns = list(data.keys())
                writer = csv.DictWriter(f,csv_columns)
                writer.writeheader()
                writer.writerow(data)
    os.chdir(cdir)

def import_source_to_df(file_path):
    """
    Reads file wirtten by write_file() to dataframe
    """
    get_extention = re.compile(r'[^.]*$')
    extention = get_extention.search(file_path).group()
    if extention == 'pkl':
        unpickle = pickle.load(open(file_path,'rb'))
        if isinstance(unpickle,dict):
            return pd.DataFrame(unpickle)
        elif isinstance(unpickle,pd.DataFrame):
            return unpickle
        else:
            raise InputError('Imprted data not of DataFrame or Dict type')
    if extention == 'json':
        jsonload = json.load(open(file_path,'rb'))
        if isinstance(jsonload,dict):
            return pd.DataFrame(jsonload)
        elif isinstance(jsonload,pd.DataFrame):
            return jsonload 
        else:
            raise InputError('Imprted data not of DataFrame or Dict type')
    if extention == 'csv':
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            print('No DataFrame output')

def import_dict(file_path):
    """
    Reads file written by write_file to dataframe
    """
    get_extention = re.compile(r'[^.]*$')
    extention = get_extention.search(file_path).group()
    if extention == 'pkl':
        unpickle_dict = pickle.load(open(file_path,'rb'))
        return unpickle_dict
    else: 
        raise InputError('import_dict() only suppords .pkl format, please\
            supply different format or implement reader in file_handler.py')
