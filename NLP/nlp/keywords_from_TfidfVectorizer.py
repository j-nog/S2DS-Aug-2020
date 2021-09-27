"""
from nationbetter.nlp import keywords_from_TfidfVectorizer

usage:
keyword_dict = keywords_from_TfidfVectorizer(docs, stop_words)

TODO: Loop over sections/pages
"""
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def keywords_from_TfidfVectorizer(document, stop_words, max_df=0.85):
    """
    docs: list of sentences
    
    create a vocabulary of words, ignore words that appear in 85% of documents, eliminate stop words

    In some of the text mining applications, such as clustering and text classification we limit the size of the vocabulary. 
    It's really easy to do this by setting max_features=vocab_size when instantiating CountVectorizer.
    """
    # settings that you use for count vectorizer will go here 
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, max_df=0.85, stop_words=stop_words)
    
    # just send in all your docs here 
    tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(document)

    # get the first vector out (for the first document) 
    first_vector_tfidfvectorizer = tfidf_vectorizer_vectors[0] # TODO not always the same

    # place tf-idf values in a pandas data frame 
    return pd.DataFrame(first_vector_tfidfvectorizer.T.todense(), index=tfidf_vectorizer.get_feature_names(), columns=["tfidf"]).sort_values(by=["tfidf"],ascending=False)
