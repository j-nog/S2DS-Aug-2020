"""
web_scraping_lib.py

A collection of functions for web scraping.
Special functions for scraping HTML documents on gov.uk/guidance
"""


#web scraping
from bs4 import BeautifulSoup,Tag,NavigableString
from urllib.parse import urlparse
import urllib.request

import warnings,datetime,os

#regex
import re

import pandas as pd

#from scraping_lib import *

def fetch_hmtl2disc(urls, path = ""):
    """
    Fetches the raw HTML for a list of URLs and writes it to disk

    urls : list of str
        list of URLs
    path : string
        output path
    """
    for url in urls:
        filename = os.path.basename(urlparse(url).path)
        urllib.request.urlretrieve(url,path + filename + ".html")


def get_links_raw(tag):
    """Extracts all links from a html page.
    FIXME: Does not work yet for relative links:
    We want all extracted urls to be absolute, not relative to the parent url

    tag : bs4.Tag
        some HTML snippet
    returns : list of str
        list of extracted urls
    """

    links = []
    for link in tag.find_all('a'):
        links.append(link.get('href'))
    return links



def scrape_url_raw(url):
    """
    Extracts raw text and links from a url

    urls : str
    returns: str, list of str
    """

    soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
    text = soup.text
    links = get_links_raw(soup)


    return text,links


def parse_html_table(table):
    """
    Parses a HTML table as represented by a bs4.Tag into a table (list of lists) of strings
    table : bs4.Tag
    returns: list
    """
    raise NotImplementedError

    assert (isinstance(table,Tag) and table.name == "table") , "Argument must be a <table> bs4.Tag!"





def pretty_print_html_table(table):
    """
    TODO: I am very unsure how well this works for tables that have more complicated content.
          The proper way to do this is probably by first converting each table entry into a string in a smart way
          and then building the table and pretty-print it.
    Pretty-prints an HTML table as represented by bs4.Tag object.
    table : bs4.Tag
    returns : string
    """
    assert (isinstance(table,Tag) and table.name == "table") , "Argument must be a <table> bs4.Tag!"

    #load HTML table into a DataFrame
    df  =  pd.read_html(str(table))[0]

    pretty_string = df.to_string(index=False)

    return pretty_string



def scrape_govuk_guidance_raw(url):
    """ Performs raw text extraction of a legal document on a https://www.gov.uk/guidance/ page
    url: str
        url of the resource
    returns: dict
        dictionary holding the URL, document title, raw text, hyperlinks and time stamp"""

    contents = {
        "URL" : url,
        "title" : "",
        "text_dump" : "",
        "hyperlinks_dump" : [],
        "timestamp" : None
    }

    try:
        web_page = urllib.request.urlopen(url)
    except:
        warnings.warn("Could not open " + url)
        return contents

    article = BeautifulSoup(web_page, 'html.parser').article
    contents["title"] = article.find(attrs={'class' : 'section-title'}).getText()
    contents["text_dump"]  = article.getText()
    contents["hyperlinks_dump"]  = get_links_raw(article)
    contents["timestamp"] = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()
    return contents


def scrape_govuk_guidance(url):
    """ Extracts sections and paragraphs of a legal document on a https://www.gov.uk/guidance/ page
    url: str
        url of the resource
    returns: dict
        dictionary holding the document title, the contents, and the hyperlinks in the document"""

    contents_dict = {
                     "URL" : url,
                     "title" : "",
                     "summary" : "",
                     "text_dump" : "",
                     "text_segmented" : [],
                     "hyperlinks_dump" : [],
                     "timestamp" : None
                    }

    #open HTML page for scraping
    try:
        web_page = urllib.request.urlopen(url)
    except:
        warnings.warn("Could not open " + url)
        return contents_dict

    contents_dict["URL"] = url
    contents_dict["timestamp"] = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()

    #part of the HTML page that only holds the legal document
    article = BeautifulSoup(web_page, 'html.parser').article

    #raw text and list of all links in the document
    contents_dict["text_dump"]  = article.getText()
    contents_dict["hyperlinks_dump"]  = get_links_raw(article)

    #title and summary of the document
    contents_dict["title"] = article.find(attrs={'class' : 'section-title'}).getText()
    contents_dict["summary"] = article.find(attrs={'class' : 'summary'}).getText()

    #get article "body" and extract its raw text
    article_body = article.find(attrs={'data-module' : 'govspeak'})

    #segment the document body into (sub)sections, plain text and tables
    #first two entries are title and summary
    text_segmented = [
        ("text",contents_dict["title"]),
        ("text",contents_dict["summary"]),
    ]

    for tag in article_body.children:
        #we might encounter NavigableString or other stuff that cannot be parsed
        if not isinstance(tag,Tag):
            continue

        if tag.name == "h2":
            text_segmented.append(("section",tag.getText()))
        elif tag.name == "h3":
            text_segmented.append(("subsection",tag.getText()))
        elif tag.name == "table":
            text_segmented.append(("table",pretty_print_html_table(tag)))
        else:
            text_segmented.append(("text",tag.getText()))



    contents_dict["text_segmented"] = text_segmented

    return contents_dict
