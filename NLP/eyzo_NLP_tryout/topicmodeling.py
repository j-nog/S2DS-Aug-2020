from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import numpy as np
import mglearn



def extract_topics(source, number_of_topics=5, number_of_wordgroups=10, length_of_wordgroup=1):
    vect=CountVectorizer(ngram_range=(length_of_wordgroup,length_of_wordgroup),stop_words='english')
    with open(source, "r", encoding='utf-8', errors='ignore') as file:
         SOURCE_TEXT = file.readlines()
    dtm=vect.fit_transform(SOURCE_TEXT)
    dtf=pd.DataFrame(dtm.toarray(),columns=vect.get_feature_names())
    lda=LatentDirichletAllocation(n_components=5)
    lda_dtf=lda.fit_transform(dtm)    
    sorting=np.argsort(lda.components_)[:,::-1]
    features=np.array(vect.get_feature_names())
    return mglearn.tools.print_topics(topics=range(number_of_topics), feature_names=features, sorting=sorting, topics_per_chunk=5, n_words=number_of_wordgroups)

