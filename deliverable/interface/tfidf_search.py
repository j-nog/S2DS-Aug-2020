import numpy as np
import pandas as pd

def search_keyword_list(keyword_list,keywords):
    """
    keyword_list : list of (str,int)
    keywords : list of str
    returns : list of str
        list of (str,int)
    """
    keywords_found = []
    for keyword in keywords:
        for label in keyword_list:
            if label[0] == keyword:
                keywords_found.append(label)

    return keywords_found


def update_keyword_list(keyword_list,new_keyword):
    """
    keyword_list : list of (str,int)
    new_keyword : (str,int)
    returns : list of (str,int)
    """

    if type(new_keyword) == str:
        new_keyword = (new_keyword,1)

    found_tf = False
    for (ii,keyword) in enumerate(keyword_list):
        if keyword[0] == new_keyword[0]:
            keyword_list[ii] = (keyword[0],keyword[1] + new_keyword[1])
            found_tf = True

    if not found_tf:
        keyword_list.append(new_keyword)

    return [keyword_list]


def get_idf_vector(corpus):
    """
    corpus : list of list of str
        list of "documents" (smallest units of text).
        A "document" is a list of distinct strings, i.e. a list of distinct terms.
    returns : ()
    """
    vocab = []
    for doc in corpus:
        for term in doc:
            if not term in vocab:
                vocab.append(term)

    n_documents = len(corpus)

    #document frequency vector
    doc_freq = np.zeros(len(vocab))

    for doc in corpus:
        for term in doc:
            doc_freq[vocab.index(term)] += 1

    idf = np.log(n_documents/(doc_freq))

    return idf,vocab,doc_freq


def get_tf_vector(terms,vocab,normalize=True):
    """
    Generates a term frequency vector
    terms : list of (str, int)
        list of terms with their number of occurence
    vocab : list of str
        list of all distinct terms. Word vectors will be constructed according to their order
    normalize : bool
        normalize the term frequency vector if true.
    """

    tf = np.zeros(len(vocab))
    for term in terms:
        if term[0] in vocab:
            tf[vocab.index(term[0])] = term[1]

    if normalize:
        tf_length = np.sqrt(np.sum(tf**2))
        if tf_length > 1e-15:
            tf /= tf_length

    return tf


def cos_similarity(v1,v2):
    """
    Cosine similarity of two vectors
    v1 : 1d array_like
    v2 : 1d array_like
    returns: float
    """
    angle = np.arccos(np.dot(v1,v2)/np.sqrt(np.sum(v1**2)*np.sum(v2**2)))
    return 1 - angle/np.pi



def tfidf_init_corpus(mycorpus):
    segments_keywords = []
    for document in mycorpus:
        for keywords in document["keywords"].tolist():
            #list of keyword - #occurences tuple to list of keywords
            if len(keywords) > 0:
                segments_keywords.append(list(list(zip(*keywords))[0]))

    idf_vector,vocab,_ = get_idf_vector(segments_keywords)

    corpus = []
    for mydocument in mycorpus:
        document = mydocument.copy()
        document["tf-idf_vector"] = document["keywords"].map(
            lambda x: get_tf_vector(x,vocab)*idf_vector
        ).copy()

        corpus.append(document)

    for document in corpus:
        #FIXME: should be just one loop that iterates over the rows of a document dataframe
        document_keywords = []
        for kw_list in document["keywords"]:
            for kw in kw_list:
                update_keyword_list(document_keywords,kw)

        document["keywords (document)"] = \
            [document_keywords.copy()]*len(document)

        document_refs = []
        for ref_list in document["references"]:
            for kw in ref_list:
                update_keyword_list(document_refs,kw)

        document["references (document)"] = \
            [document_keywords.copy()]*len(document)

        document_records = []
        for record_list in document["needed records"]:
            for kw in record_list:
                update_keyword_list(document_records,kw)

        document["needed records (document)"] = \
            [document_keywords.copy()]*len(document)

        document_refs_urls = []
        for ref_urls_list in document["reference urls"]:
            document_refs_urls.extend([x for x in ref_urls_list if not x in document_refs_urls])

        document["reference urls (document)"] = \
            [document_refs_urls.copy()]*len(document)

        document["tf-idf_vector_document"] = \
            [get_tf_vector(document_keywords,vocab)*idf_vector]*len(document)

    return corpus,idf_vector,vocab

def search_corpus_tfidf(query_keywords,corpus,idf_vector,vocab,level = "segment",sort_by_relevance=True):
    """
    Searches a given document corpus for keywords
    corpus : list of pandas.DataFrame
    query_keywords : list of str
    idf_vector : 1d array-like
    term_list : list of str
    sort_by_relevance : bool, default False
        If true, sorts the result by the number of keywords found in decending order
    returns : pandas.DataFrame
        A table that hold all the subsections of the documents in which the keywords were found
    """
    search_result = None


    query_keywords_tuples = list(zip(query_keywords,len(query_keywords)*[1]))
    query_tfidf_vector = idf_vector*get_tf_vector(query_keywords_tuples,vocab,normalize=True)


    for mydocument in corpus:
        document = mydocument.copy()


        if level == "segment":
            document["keywords found"] = document["keywords"].map(lambda x: search_keyword_list(x,query_keywords)).copy()
            document = document[document["keywords found"].map(lambda x: x != [])]
            document["relevance"] = \
                document["tf-idf_vector"].map(
                    lambda x:
                    cos_similarity(x,query_tfidf_vector)
                ).copy()
            document = document.drop(["needed records (document)","reference urls (document)","references (document)","keywords (document)"],axis=1)

        elif level == "document":
            document = document[0:1]
            document["keywords found"] = document["keywords (document)"].map(lambda x: search_keyword_list(x,query_keywords)).copy()

            document["relevance"] = \
                document["tf-idf_vector_document"].map(
                    lambda x:
                    cos_similarity(x,query_tfidf_vector)
                ).copy()
            document = document.drop(
                ["page_no","section title","subsection title","subsubsection title","keywords","text","keywords (document)"]
                ,axis=1)
            document = document.drop(["needed records","reference urls","references"],axis=1)
            document = document.drop(["section","subsection","subsubsection"],axis=1)
        else:
            raise ValueError("level must be either \"document\" or \"segment\" ")


        document = document.drop(["tf-idf_vector","tf-idf_vector_document"],axis=1)


        if search_result is None:
            search_result = document
        else:
            search_result = pd.concat([search_result,document],ignore_index = True)

    #sort by cosine similarity
    if sort_by_relevance:
        search_result = search_result.sort_values(by = "relevance",ascending=False,ignore_index = True)
        #pass

    return search_result