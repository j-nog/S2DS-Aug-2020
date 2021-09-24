
"""
scrape_immigration_rules.py

Scrape all the "Immigration Rules" documents from https://www.gov.uk/guidance/immigration-rules
and pickle the resulting DataFrame to immigration_rules_scrape.pickle
"""

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from web_scraping_lib import *

import pandas as pd
from scraping_lib import scrape_documents

import pickle

immigration_rules_url = "https://www.gov.uk/guidance/immigration-rules"

soup = BeautifulSoup(urllib.request.urlopen(immigration_rules_url), 'html.parser')
tag = soup.article.find(attrs={'class' : 'section-list'})
links = get_links_raw(tag,immigration_rules_url)

scrape_df = pd.DataFrame(scrape_documents(links))



with open('immigration_rules_scrape.pickle','wb') as f:
    pickle.dump(scrape_df,f, pickle.HIGHEST_PROTOCOL)
