"""
text_wrangling_utils.py

A collection of functions for wrangling scraped text.
"""

import pandas as pd
from .file_handler import get_inner_folder, write_files, import_dict

def map_df(f,x_list):
    """ Similar to built-in "map()" but returns a DataFrame instead of a list.
    f : function
        function that returns a dictionary
    x_list : list
        arguments for f
    returns: pandas.DataFrame
    """
    dicts = [f(x) for x in x_list]
    df = pd.DataFrame(dicts)

    return df


def pretty_print_string_table(string_table):
    """
    Pretty-prints a table of strings
    string_table : list of list of str
    """
    df = pd.DataFrame(string_table[1:],columns = string_table[0])
    pretty_string = df.to_string(index=False)

    return pretty_string


def build_segments_df(in_file,out_path):
    """
    Build a pandas.DataFrame from a list of text segments.
    segments : list of tuples
        each touple has the struncture (label,string),
        where label can be either "text","header","subheader","table". All other labels are treated as "text"
    """
    write_path = get_inner_folder(out_path,'formatted_html_dfs')
    segments = import_dict(in_file)["text_segmented"]

    print('Extracting contents of {}, to DataFrame.'.format(in_file))
    section_cntr = 0
    subsection_cntr = 0
    segments_dict = {"section" : [], "subsection" : [],  "string" : []}

    for (ii,segment) in enumerate(segments):

        if segment[0] == "section":
            section_cntr = section_cntr + 1
            subsection_cntr = 0
        elif segment[0] == "subsection":
            subsection_cntr = subsection_cntr + 1





        segments_dict["section"].append(section_cntr)
        segments_dict["subsection"].append(subsection_cntr)
        segments_dict["string"].append(segment[1])

    segments_df = pd.DataFrame(segments_dict)
    outname0 = in_file[0:5]
    outname1 = in_file[5:]
    outname = outname0+outname1.replace(" ","_").replace(":","")
    write_files(segments_df,write_path,outname,'pickle')
    #return segments_df

def build_segments_tree(text_segments):
    """
    Build a tree that represents the document structure from a list of text elements
    TODO: Implement this
    """
    raise NotImplementedError
