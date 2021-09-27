"""
from nationbetter.nlp import keywords_from_TfidfTransformer

usage:
keyword_dict = keywords_from_TfidfTransformer(docs, stop_words)
"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def keywords_from_TfidfTransformer(document, stop_words, max_df=0.85):
    """
    document : list of sentences for each section/page from WHOLE document ["docs1", "docs2", "docs3"]
               docs1-> sentences from section1/page1
               docs2-> sentences from section2/page2
               ...
    """
    # create a CountVectorizer to count the number of words (term frequency)
    cv = CountVectorizer(max_df=0.85, stop_words=stop_words)
    # this steps generates word counts for the words in your docs (WHOLE DOCUMENTS)
    word_count_vector = cv.fit_transform(document)

    # compute the IDF values by calling tfidf_transformer.fit(word_count_vector) on the word counts
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True) 
    tfidf_transformer.fit(word_count_vector)

    # you only needs to do this once    
    feature_names = cv.get_feature_names()
    
    # Once you have the IDF values, you can now compute the tf-idf scores for any document or set of documents.
    results = {}
    for i in range(len(document)):
        doc = document[i]
        # generate tf-idf for the given document
        tf_idf_vector = tfidf_transformer.transform(cv.transform([doc]))    
        #sort the tf-idf vectors by descending order of scores
        sorted_items = sort_coo(tf_idf_vector.tocoo())
        #extract only the top n; n here is 10
        keywords = extract_topn_from_vector(feature_names,sorted_items,10)
        results[i] = keywords
    return results

def sort_coo(coo_matrix):
    """
    method essentially sorts the values in the vector while preserving the column index
    """
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """
    get the feature names and tf-idf score of top n items
    """
    #use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    for idx, score in sorted_items:
        fname = feature_names[idx]        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    return results