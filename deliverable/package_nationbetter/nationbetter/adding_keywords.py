import pandas as pd
import pickle
import os, re
from geotext import GeoText
from collections import Counter
from pathlib import Path
from .file_handler import get_inner_folder, import_source_to_df, write_files
pd.options.mode.chained_assignment = None
from nationbetter.keywords import *
# Imporging the keywords
#from ../keywords import *
def get_tagged_corpus(pdf_folder, html_folder, html_dicts, out_path):
    print('Adding keys to the corpus and storing in {}'.format(out_path))
    # importing the files
    formatted_html_path = html_folder
    formatted_html_pkls = os.listdir(html_folder)
    formatted_pdf_path = pdf_folder
    formatted_pdf_pkls = os.listdir(pdf_folder)
    raw_html_dicts = html_dicts
    html_raw_dict_pickles = os.listdir(raw_html_dicts)

    ####################################################
    # loading and formatting pdfs
    ####################################################
    pdfs =[]
    for file in formatted_pdf_pkls:
        df = pickle.load(open(os.path.join(formatted_pdf_path,file),'rb'))
        pdfs.append(df)
        df[df['page_no']==1]

    for df in pdfs:
        title_idx =df[(df['text_type']=='title')&(df['page_no']==1)].index[0]
        has_sub = df[(df['text_type']=='subtitle')&(df['page_no']==1)].index
        if title_idx != 0:
            df.drop([title_idx-1],inplace = True)
        if list(has_sub):
            if has_sub[0]>title_idx:
                new_title= df.iloc[title_idx].text + df.iloc[has_sub[0]].text
                df.at[0,'text']= new_title

    # list of pdf URLs
    pdf_urls = [pdfs[i]['url'][1] for i in range(len(pdfs))]
    # Drop non title first lines
    for df in pdfs:
        title_index = df[df['text_type']=='title'].index.min()
        df.drop(df[~(df.index>=title_index)].index,inplace=True)

    #Renaming the columns in the dataframe with the convention of html
    keylist = []
    for df in pdfs:
        keylist.append(df.keys())
    for df_no in range(len(pdfs)):
        find_sec = re.compile(r'\w*title$')
        find=list(filter(None,[find_sec.search(key) for key in keylist[df_no]]))
        old_keys = [key.group() for key in find]
        #if the dataframe of pdfs[0] is fixed and keys still need to be dropped
        # insert here some code that renames missing keys and columns
        # ['title','subsubsection'] -> ['title','subtitle']
        keep_keys = keylist[df_no].drop(old_keys)
        find_sec = re.compile(r'(title)$')
        final_keys = [find_sec.sub(r'section',key) for key in keylist[df_no]]
        rename_keys = pd.Index(final_keys).drop(keep_keys)
        rename_dict = dict(zip(old_keys,rename_keys))
        pdfs[df_no].rename(columns = rename_dict,inplace = True)

    #write function that can be iterated over to obtain section title columns
    #for single df
    # df_no = 1
    # Sorting the keys into agg_keys, which will generate the column names
    # and dropping unwanted keys
    keylist = []
    for df in pdfs:
        keylist.append(df.keys())

    def get_title_col_pdf(df,sec_col='text'):
        '''
        Taking a column (of section counters) and check weither a section
        transition occurs. If yes store in column [(sub)*section]_title
        the tite (assuming it happpends) on the first line of the section
        '''
        #Checking if the (sub)section title changes if yes return true
        is_sec_title = (df[sec_col]-df[sec_col].shift().bfill()).astype(bool)
        colname = sec_col + ' title'
        return is_sec_title, colname


    for num, df in enumerate(pdfs):
        #get the keys
        keylist = df.keys()
        find_sec = re.compile(r'\w*section$')
        find=list(filter(None,[find_sec.search(key) for key in keylist]))
        agg_keys = [key.group() for key in find]
        sec_keys = agg_keys + ['page_no','text','url']
        #reduce the dataframe
        df = df[sec_keys]

        #call function
        for key in agg_keys:
            is_sec_title, colname = get_title_col_pdf(df,key)
            #Selects string column where is_sec_title true, returns section name
            titlecol = df[is_sec_title].text.replace('\s+', ' ', regex=True).str.strip()
            titlecol.name = colname
            df = pd.concat([df,titlecol],axis = 1)
            df[colname].fillna(method='ffill',inplace=True)

        #Generate dict for aggregation of text in (sub)*sections
        dex = df.keys().drop(agg_keys+['text'])
        agg_fn = ['first' for no_dex in range(len(dex))]
        agg_arg = dict(zip(dex,agg_fn))
        agg_arg.update({'text':' '.join})
        df.groupby(agg_keys,as_index = False).agg(agg_arg)
       # df.rename(columns={'text':'string'},inplace=True)
        pdfs[num]=df

    # indexing in all dataframes should start at 0
    pdfs = [pdfs[i].reset_index() for i in range(len(pdfs))]

    # list of all pdf titles
    pdf_titles = []
    for df in pdfs:
        title_loc = df.index.min()
        pdf_titles.append(df.text.replace('\s+', ' ', regex=True).str.strip()[title_loc])
    # the biggest segment has to be "section"
    for i in range(len(pdfs)):
        if 'section' not in pdfs[i].columns:
            if 'subsection' in pdfs[i].columns:
                pdfs[i]=pdfs[i].rename(columns = {'subsection':'section'})
                pdfs[i]=pdfs[i].rename(columns = {'subsection title':'section title'})
                if 'subsubsection' in pdfs[i].columns:
                    pdfs[i]=pdfs[i].rename(columns = {'subsubsection':'subsection'})
                    pdfs[i]=pdfs[i].rename(columns = {'subsubsection title':'subsection title'})
            elif 'subsubsection' in pdfs[i].columns:
                pdfs[i]=pdfs[i].rename(columns = {'subsubsection':'section'})
                pdfs[i]=pdfs[i].rename(columns = {'subsubsection title':'section title'})
    # removing index column for PDFs
    for i in range(len(pdfs)):
        pdfs[i] = pdfs[i].drop('index', 1)

    ####################################################
    # loading and formatting HTMLS
    ####################################################
    htmls =[]
    for file in formatted_html_pkls:
        df = pickle.load(open(os.path.join(formatted_html_path,file),'rb'))
        htmls.append(df)
    def get_title_col_html(df,sec_col='string'):
        #Checking if the (sub)section title changes if yes return true
        is_sec_title = (df[sec_col]-df[sec_col].shift().bfill()).astype(bool)
        colname = sec_col + ' title'
        #Selects string column where is_sec_title true, returns section name
        df[colname]= df[is_sec_title].string
        df[colname].fillna(method='ffill',inplace = True)

    def agg_subsections_html(df):
        #get columns which need to be added
        list_to_new_keys = ['section','subsection']
        for key in list_to_new_keys:
            get_title_col_html(df,key)
        df.groupby(['section','subsection'],as_index = False).agg({'string':' '.join,'section title':'first','subsection title':'first'},inplace = True)

    for df in htmls:
        agg_subsections_html(df)
    # rename column "string" in the html dataframes as "text"
    for i in range(len(htmls)):
        htmls[i].rename(columns = {'string':'text'}, inplace = True)

    # html titles and URLs
    html_titles = []
    html_urls = []
    for i in range(len(htmls)):
        raw_dict = pickle.load(open(os.path.join(raw_html_dicts,html_raw_dict_pickles[i]),'rb'))
        html_titles.append(raw_dict["title"])
        html_urls.append(raw_dict["URL"])

    ####################################################
    # Adding Keywords
    ####################################################

    # the columns for the labels are added, some entries are set to empty lists
    # for html
    for i in range(len(htmls)):
        htmls[i]['document title'] = html_titles[i]
        htmls[i]['document url'] = html_urls[i]
        htmls[i]['document type'] = "html"
        htmls[i]['keywords'] = [[] for _ in range(len(htmls[i]))]
        htmls[i]['needed records'] = [[] for _ in range(len(htmls[i]))]
        htmls[i]['references'] = [[] for _ in range(len(htmls[i]))]
        htmls[i]['reference urls'] = [[] for _ in range(len(htmls[i]))]

    # for pdf
    for i in range(len(pdfs)):
        pdfs[i]['document title'] = pdf_titles[i]
        pdfs[i]['document url'] = pdf_urls[i]
        pdfs[i]['document type'] = "pdf"
        pdfs[i]['keywords'] = [[] for _ in range(len(pdfs[i]))]
        pdfs[i]['needed records'] = [[] for _ in range(len(pdfs[i]))]
        pdfs[i]['references'] = [[] for _ in range(len(pdfs[i]))]
        pdfs[i]['reference urls']=[[] for _ in range(len(pdfs[i]))]

    # find mentioning of "Appendix XYZ and "Part XYZ"
    pattern_appendix = r"[Aa]ppendix [0-9]*[A-Za-z]*[-]*\s*[A-Za-z]*\s*[(]*[A-Za-z]*\s*[A-Za-z]*[)]*"
    pattern_part = r"[Pp]art [0-9]*[A-Za-z]*\s*[A-Za-z]*\s*[(]*[A-Za-z]*\s*[A-Za-z]*[)]*"

    # the list of all document titles is updated with all expressions from pattern_appendix
    # and pattern_part that appear in the list of documents

    ref_in_title_list = html_titles + pdf_titles

    for i in range(len(htmls + pdfs)):

        ref_appendix = re.findall(pattern_appendix, str(ref_in_title_list[i]) )
        ref_part = re.findall(pattern_part, str(ref_in_title_list[i]) )

        if ref_part!=[]:
            ref_in_title_list+= ref_part

        if ref_appendix!=[]:
            ref_in_title_list+= ref_appendix

        else:
            continue

    keyword_processor_ref.add_keywords_from_list(ref_in_title_list)

    # keywords for htmls
    for i in range(len(htmls)):
        doctitle=html_titles[i]
        for j in range(len(htmls[i])):
            sectitle=str(htmls[i]['section title'][j])
            subsectitle=str(htmls[i]['subsection title'][j])
            # more weight is put to words appearing in titles
            text=3*(doctitle + " ")  + 2*(sectitle + " ")+ subsectitle + " " +htmls[i]['text'][j]
            #The regional keywords are updated with all names of countries except "United Kingdom"
            countrylist=list(Counter(GeoText(text).countries).items())
            count_minus_uk = [t for t in countrylist if (t[0] != 'United Kingdom')]
            keywords_all=list(Counter(keyword_processor_all.extract_keywords(text)).items())
            htmls[i]['keywords'][j]=keywords_all +count_minus_uk
            keywords_rec=list(Counter(keyword_processor_rec.extract_keywords(text)).items())
            htmls[i]['needed records'][j]=keywords_rec
            keywords_ref = list(Counter(keyword_processor_ref.extract_keywords(text)).items())
            # removing self-references
            keywords_refminusself = [t for t in keywords_ref if (t[0] not in subsectitle) if (t[0] not in sectitle) if (t[0] not in doctitle)]
            htmls[i]['references'][j]=keywords_refminusself
    # keywords for pdf

    for i in range(len(pdfs)):
        doctitle = pdf_titles[i]
        for j in range(len(pdfs[i])):
            sectitle = ""
            if 'section title' in pdfs[i].columns:
                sectitle = str(pdfs[i]['section title'][j])
            subsectitle = ""
            if 'subsection title' in pdfs[i].columns:
                subsectitle = str(pdfs[i]['subsection title'][j])
            subsubsectitle = ""
            if 'subsubsection title' in pdfs[i].columns:
                subsubsectitle = str(pdfs[i]['subsubsection title'][j])
            subsubsubsectitle = ""
            if 'subsubsubsection title' in pdfs[i].columns:
                subsubsubsectitle = str(pdfs[i]['subsubsubsection title'][j])
            subsubsubsubsectitle = ""
            if 'subsubsubsubsection title' in pdfs[i].columns:
                subsubsubsubsectitle = str(pdfs[i]['subsubsubsubsection title'][j])
            # more weight is put to words appearing in titles
            text = (pdfs[i]['text'][j]  + " " + 3*(doctitle + " ")  + 2*(sectitle + " ")
                    + subsectitle + " " + subsubsectitle + " "
                    + subsubsubsectitle + " " + subsubsubsubsectitle)
            #The regional keywords are updated with all names of countries except "United Kingdom"
            countrylist=list(Counter(GeoText(text).countries).items())
            count_minus_uk = [t for t in countrylist if (t[0] != 'United Kingdom')]
            keywords_all=list(Counter(keyword_processor_all.extract_keywords(text)).items())
            pdfs[i]['keywords'][j]=keywords_all +count_minus_uk
            keywords_rec=list(Counter(keyword_processor_rec.extract_keywords(text)).items())
            pdfs[i]['needed records'][j]=keywords_rec
            keywords_ref = list(Counter(keyword_processor_ref.extract_keywords(text)).items())
            # removing self-references
            keywords_refminusself = [t for t in keywords_ref if (t[0] not in subsectitle) if (t[0] not in sectitle) if (t[0] not in doctitle)]
            pdfs[i]['references'][j]=keywords_refminusself

    # update column "reference urls" with urls corresponding to titles that appear in the "references" column

    all_titles = html_titles + pdf_titles
    all_urls = html_urls + pdf_urls

    #for html documents
    for i in range(len(htmls)):
        for j in range(len(htmls[i])):
            tuple_list= htmls[i]['references'][j]
            url_for_ref = []
            if tuple_list != []:
                value_list = [itm[0] for itm in tuple_list]
                for ref in  value_list:
                    for longtitle in all_titles:
                        if ref in longtitle:
                            idx = all_titles.index(longtitle)
                            item = all_urls[idx]
                            url_for_ref.append(item)
            htmls[i]['reference urls'][j] = url_for_ref

    #for PDFs
    for i in range(len(pdfs)):
        for j in range(len(pdfs[i])):
            tuple_list= pdfs[i]['references'][j]
            url_for_ref = []
            if tuple_list != []:
                value_list = [itm[0] for itm in tuple_list]
                for ref in  value_list:
                    for longtitle in all_titles:
                        if ref in longtitle:
                            idx = all_titles.index(longtitle)
                            item = all_urls[idx]
                            url_for_ref.append(item)
            pdfs[i]['reference urls'][j] = url_for_ref

    # The first pdf has such a different format that we have to leave it out for now.

    list_of_dataframes = pdfs[:1] + htmls
    outfile = 'labeled_corpus.pkl'
    write_files(list_of_dataframes,out_path,outfile)
    # with open('labeled_corpus.pickle','wb') as f:
    #     pickle.dump(list_of_dataframes,f, pickle.HIGHEST_PROTOCOL)
