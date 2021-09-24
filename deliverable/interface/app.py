"""
USAGE:
> cd interface (go to the folder where interface resides)
> python app.py

Open browser and paste the given localhost, e.g. http://127.0.0.1:5000
"""
from flask import Flask, request, render_template, session, redirect
import pandas as pd
import os
import sys
import pickle

from nationbetter.keywords import *
#from nationbetter.tfidf_search import search_corpus_tfidf
from tfidf_search import *

app = Flask(__name__)

'''
TODO : point the location of DATA
'''
DATA_NAME = '../data_nationbetter/labeled_corpus.pkl'
#DATA_NAME = './data/labeled_immigration_rules.pickle'

def clean_up_corpus(mycorpus):
    corpus = []

    for mydocument in mycorpus:
        document = mydocument.copy()
        if document["document type"][0] == "html":
            document.insert(4,"subsubsection",0)
            document.insert(5,"subsubsection title","")
            document.insert(6,"page_no",1)
        elif document["document type"][0] == "pdf":
            if "subsection" not in document.columns:
                document.insert(1,"subsection",0)
            if "subsubsection" not in document.columns:
                document.insert(2,"subsubsection",0)

            document = document[
                ["section","subsection","subsubsection","page_no","text",
                 "document title","document url","document type",
                 "keywords","needed records","references","reference urls"]
            ]

            document.insert(1,"section title","")
            document.insert(3,"subsection title","")
            document.insert(5,"subsubsection title","")

        corpus.append(document)

    return corpus

with open(DATA_NAME,'rb') as f:
    labeled_corpus = pickle.load(f)

labeled_corpus = clean_up_corpus(labeled_corpus)
corpus_tfidf,idf_vector,vocab = tfidf_init_corpus(labeled_corpus)

# lists related to the dropdowns
list_immigration_status = dropdown_dict['immigration status']
list_region = dropdown_dict['region']
list_role = dropdown_dict['role']
list_company_type = dropdown_dict['company type']
list_company_body = dropdown_dict['company body']
list_regulatory_body = dropdown_dict['regulatory body']
list_education = dropdown_dict['education']
list_profession = dropdown_dict['profession']
list_skill_level = dropdown_dict['skill level']
list_position = dropdown_dict['position']
list_relation = dropdown_dict['relation']
list_general = dropdown_dict['general']
list_SOC_codes = dropdown_dict['SOC codes']
list_SOC_titles = dropdown_dict['SOC titles']
list_taxonomy = ['document', 'segment']

@app.route('/', methods=('POST', 'GET'))
def query():
    '''
    Set queries withing query.html
    Route to the results.html
    '''
    error = ''
    if request.method == 'POST':
        keywords = str(request.form.get('keywords'))
        session['keywords'] = keywords
        select_immigration_status = str(request.form.get('select_immigration_status'))
        session['select_immigration_status'] = select_immigration_status
        select_region = str(request.form.get('select_region'))
        session['select_region'] = select_region
        select_role = str(request.form.get('select_role'))
        session['select_role'] = select_role
        select_company_type = str(request.form.get('select_company_type'))
        session['select_company_type'] = select_company_type
        select_company_body = str(request.form.get('select_company_body'))
        session['select_company_body'] = select_company_body
        select_regulatory_body = str(request.form.get('select_regulatory_body'))
        session['select_regulatory_body'] = select_regulatory_body
        select_education = str(request.form.get('select_education'))
        session['select_education'] = select_education
        select_profession = str(request.form.get('select_profession'))
        session['select_profession'] = select_profession
        select_skill_level = str(request.form.get('select_skill_level'))
        session['select_skill_level'] = select_skill_level
        select_position = str(request.form.get('select_position'))
        session['select_position'] = select_position
        select_relation = str(request.form.get('select_relation'))
        session['select_relation'] = select_relation
        select_general = str(request.form.get('select_general'))
        session['select_general'] = select_general
        select_SOC_codes = str(request.form.get('select_SOC_codes'))
        session['select_SOC_codes'] = select_SOC_codes
        select_SOC_titles = str(request.form.get('select_SOC_titles'))
        session['select_SOC_titles'] = select_SOC_titles
        select_taxonomy = str(request.form.get('select_taxonomy'))
        session['select_taxonomy'] = select_taxonomy
        return redirect('results')
    else:
        error = 'No inputs provided, please check your inputs!'
    return render_template('query.html',
                           list_immigration_status = list_immigration_status,
                           list_region = list_region,
                           list_role = list_role,
                           list_company_type = list_company_type,
                           list_company_body = list_company_body,
                           list_regulatory_body = list_regulatory_body,
                           list_education = list_education,
                           list_profession = list_profession,
                           list_skill_level = list_skill_level,
                           list_position = list_position,
                           list_relation = list_relation,
                           list_general = list_general,
                           list_SOC_codes = list_SOC_codes,
                           list_SOC_titles = list_SOC_titles,
                           list_taxonomy = list_taxonomy,
                           error = error)

@app.route('/results', methods=('POST', 'GET'))
def results():
    '''
    Within POST method received in query page, perform search and display the results
    '''
    # list of keywords
    keywords = session['keywords']
    keywords = [k.strip() for k in keywords.split(',')]
    select_immigration_status = [session['select_immigration_status']]
    select_region = [session['select_region']]
    select_role = [session['select_role']]
    select_company_type = [session['select_company_type']]
    select_company_body = [session['select_company_body']]
    select_regulatory_body = [session['select_regulatory_body']]
    select_education = [session['select_education']]
    select_profession = [session['select_profession']]
    select_skill_level = [session['select_skill_level']]
    select_position = [session['select_position']]
    select_relation = [session['select_relation']]
    select_general = [session['select_general']]
    select_SOC_codes = [session['select_SOC_codes']]
    select_SOC_titles = [session['select_SOC_titles']]
    iterables = [select_immigration_status, select_region, select_role,
                 select_company_type, select_company_body, select_regulatory_body,
                 select_education, select_profession, select_skill_level,
                 select_position, select_relation, select_general,
                 select_SOC_codes, select_SOC_titles]

    for ll in (zip(*iterables)):
        for i, l in enumerate(ll):
            if l != 'Choose...':
                keywords.append(ll[i])

    message = ''
    # if keywords is like ['' ,'   ', ' ']
    if not any(s.strip() for s in keywords):
        # Empty dataframe will return
        # No need to perform query ?
        #print(keywords, file=sys.stderr)
        tables = []
        titles = 0
        len_df_query = -1
        message = 'Empty result has returned due to the empty search queries (%r)!' % keywords
    else:
        # Set input variables
        select_taxonomy = session['select_taxonomy']
        if select_taxonomy == 'Choose...':
            select_taxonomy = list_taxonomy[0] # 'document' is default?
        # Start keyword searches
        #df = pd.read_pickle(DATA_PATH + DATA_NAME)
        #df_query = search_corpus_keywords(df, keywords, level=select_taxonomy)
        df_query = search_corpus_tfidf(keywords,corpus_tfidf,idf_vector,vocab,sort_by_relevance=True,level=select_taxonomy)
        len_df_query = len(df_query)
        if len_df_query == 0:
            message = 'No results have been found for your search queries (%r)!' % keywords
        tables=[df_query.to_html(classes='data_query', index=False, render_links=True).replace('\\n','<br>')]
        titles=df_query.columns.values

    return render_template('results.html',keywords=keywords, len_df_query=len_df_query,
                           tables=tables, titles=titles, message=message)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)

    app.run()
