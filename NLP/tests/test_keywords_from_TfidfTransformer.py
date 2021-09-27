# append package path
import sys
sys.path.append("D:\\data-science\\S2DS")

from nationbetter.nlp import keywords_from_TfidfTransformer

import pandas as pd
df = pd.read_csv("../input/2020-07-16_Tier-2-5-sponsor-guidance_Jul-2020_v1.0_data.csv", index_col=0)

import re

def clean_doc(doc):
    """
    Cleans the document from unneecessary chars/words, etc.
    
    TODO : maybe first-level / second-level cleaning
    """
    doc = re.sub(r"[\t\n]+", "", doc)                                                   # find & replace \t and \n with empty string
    doc = re.sub(r"[^\x00-\x7F]+", " ", doc)                                            # remove non-ascii chars
    doc = re.sub(r" +", " ", doc)                                                       # remove dublicate spaces
    doc = doc.strip()                                                                   # strip leading/trailing spaces
    doc = re.sub(r"(Page)\s\d{1,2,3}\s\w+\s\d{1,3}\s(Tiers 2 and 5: guidance for sponsors - version 07/20)", "", doc)  # TODO
    doc = re.sub(r"(Annex)\s(\w)", r"\1_\2", doc)                                       # find & replace Annex 9 -> Annex_9 
    doc = re.sub(r"(Appendix)\s(\w)", r"\1_\2", doc)                                    # find & replace Apeendix 9 -> Appendix_9 
    doc = re.sub(r"(Table)\s(\w)", r"\1_\2", doc)                                       # find & replace Table 9 -> Table_9
    doc = re.sub(r"(Tier|Tiers)\s(\d)\s(and|or|and/or)\s(\d)", r"\1_\2_\3_\4", doc)     # find & replace Tier 2 and 5 -> Tier_2_and_5
    doc = re.sub(r"(Tier)\s(\d)", r"\1_\2", doc)                                        # find & replace Tier 4 -> Tier_4
    doc = re.sub(r"(\d{1,2})\s(January|February|March)\s(\d{4})", r"\1_\2_\3", doc)     # combine dates -> 1_June_2020
    doc = re.sub(r"(\d{1,2})\s(April|May|June)\s(\d{4})", r"\1_\2_\3", doc)             # combine dates 
    doc = re.sub(r"(\d{1,2})\s(July|August|September)\s(\d{4})", r"\1_\2_\3", doc)      # combine dates 
    doc = re.sub(r"(\d{1,2})\s(October|November|December)\s(\d{4})", r"\1_\2_\3", doc)  # combine dates 
    return doc
    
df.raw_text = df.raw_text.apply(lambda x:clean_doc(x))
docs = df.raw_text.to_list()
print ("Number of pages : " , len(docs))

from nltk.corpus import stopwords
stop_words = stopwords.words('english')

# dummy list of keywords to be EXCLUDED
list_of_keywords = ['from', 'subject', 're', 'edu', 'use'] 
stop_words.extend(list_of_keywords)

keyword_dict = keywords_from_TfidfTransformer(docs, stop_words)