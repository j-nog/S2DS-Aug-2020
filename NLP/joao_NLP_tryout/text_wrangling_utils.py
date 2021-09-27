import pandas as pd

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


def build_segments_df(segments):
    """
    Build a pandas.DataFrame from a list of text segments.
    segments : list of tuples
        each touple has the struncture (label,string),
        where label can be either "text","header","subheader","table". All other labels are treated as "text"
    """
    section_cntr = 0
    subsection_cntr = 0

    segments_dict = {"section" : [], "subsection" : [], "is table" : [], "string" : []}

    for (ii,segment) in enumerate(segments):

        if segment[0] == "section":
            section_cntr = section_cntr + 1
            subsection_cntr = 0
        elif segment[0] == "subsection":
            subsection_cntr = subsection_cntr + 1


        if segment[0] == "table":
            segments_dict["is table"].append(True)
        else:
            segments_dict["is table"].append(False)

        segments_dict["section"].append(section_cntr)
        segments_dict["subsection"].append(subsection_cntr)
        segments_dict["string"].append(segment[1])

    segments_df = pd.DataFrame(segments_dict)

    return segments_df

def build_segments_tree(text_segments):
    """
    Build a tree that represents the document structure from a list of text elements
    TODO: Implement this
    """
    raise NotImplementedError
