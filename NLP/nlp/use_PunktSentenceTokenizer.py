"""
from nationbetter.nlp import use_PunktSentenceTokenizer.py

usage:
sentences = use_PunktSentenceTokenizer(docs, abbreviations)
"""
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

def use_PunktSentenceTokenizer(doc, abbreviations):
    punkt_param = PunktParameters()
    abbreviation = abbreviations
    punkt_param.abbrev_types = set(abbreviation)
    tokenizer = PunktSentenceTokenizer(punkt_param)
    tokenizer.train(doc)
    sentences = tokenizer.tokenize(doc)
    return sentences