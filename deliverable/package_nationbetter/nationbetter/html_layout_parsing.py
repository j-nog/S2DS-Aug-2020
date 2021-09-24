"""
web_scraping_lib.py

A collection of functions for web scraping.
Special functions for scraping HTML documents on gov.uk/guidance
"""


#web scraping
from bs4 import BeautifulSoup,Tag,NavigableString

#TODO: Use just one library for HTTP requests!
from urllib.parse import urlparse
import urllib.request
import requests
import warnings,datetime,os
from .file_handler import get_inner_folder, write_files
#regex
import re
import pandas as pd

#from scraping_lib import *

def get_media_type(url):
    """
    FIXME: Is this a clean way of doing it? Shouldn't the request be closed?
    Retrieves the media type of the resource the url is referring to.
    url : str
    returns : str
    """
    try:
        content_type = requests.get(url).headers['content-type']
    except:
        warnings.warn("Could not open " + url)
        return None

    # the content type may be of the form 'media-type; encoding'
    # we just want the media type
    sep_idx = content_type.find(";")
    if sep_idx == -1:
        return content_type
    else:
        return content_type[:sep_idx]

def timestamp_utc():
    # returns the current UTC time in ISO format
    # returns : str
    return datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()

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


def get_links_raw(tag,url = ""):
    """Extracts all links from a html page.
    TODO: Does not work yet for relative links:
    We want all extracted urls to be absolute, not relative to the parent url

    tag : bs4.Tag
        some HTML snippet
    url : str
        If non-empty, relative links are treated as relative to the specified
        url and converted to absolute ones
    returns : list of str
        list of extracted urls
    """
    links = []
    for link in tag.find_all('a'):
        link = link.get('href')
        if url != "":
            if link[0] == "/":
                links.append(urllib.parse.urljoin(url,link))
            else:
                links.append(link)
        else:
            links.append(link)

    return links



def scrape_html_raw(url):
    """
    Extracts raw text and links from a URL

    urls : str
    returns: dict
        dictionary holding raw text, hyperlinks and time stamp
    """

    soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')


    contents_dict = {}
    contents_dict["text_dump"]  = soup.getText()
    contents_dict["hyperlinks_dump"]  = get_links_raw(soup,url)
    contents_dict["timestamp"]  =  timestamp_utc()

    return contents_dict


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
    contents["hyperlinks_dump"]  = get_links_raw(article,url)
    contents["timestamp"] = timestamp_utc()

    return contents


def scrape_govuk_guidance(url,out_path,out_type='pickle'):
    """
    Extracts sections and paragraphs of a legal document on a https://www.gov.uk/guidance/ page
    url: str
        url of the resource
    returns: dict
        dictionary holding the scraped contents
    """
    write_path = get_inner_folder(out_path,'raw_html_dicts')
    print('Extracting contents of {}, to dict.'.format(url))
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
    contents_dict["timestamp"] = timestamp_utc()

    #part of the HTML page that only holds the legal document
    article = BeautifulSoup(web_page, 'html.parser').article

    #raw text and list of all links in the document
    contents_dict["text_dump"]  = article.getText()
    contents_dict["hyperlinks_dump"]  = get_links_raw(article,url)

    #title and summary of the document
    contents_dict["title"] = article.find(attrs={'class' : 'section-title'}).getText()
    contents_dict["summary"] = article.find(attrs={'class' : 'summary'}).getText()

    #get article "body" and extract its raw text
    article_body = article.find(attrs={'data-module' : 'govspeak'})

    #segment the document body into (sub)sections, plain text and tables

    #first two entries are title and summary
    text_segmented = [
        ("text",contents_dict["title"] + "\n" +  contents_dict["summary"]),
    ]
    #true if the previous item in the iteration was plain text
    prev_was_text = True

    for tag in article_body.children:
        #we might encounter a NavigableString or other stuff that cannot be parsed
        if not isinstance(tag,Tag):
            continue

        if tag.name == "h2":
            text_segmented.append(("section",tag.getText()))
            prev_was_text = False
        elif tag.name == "h3":
            text_segmented.append(("subsection",tag.getText()))
            prev_was_text = False
        elif tag.name == "table":
            text_segmented.append(("table",pretty_print_html_table(tag)))
            prev_was_text = False
        else:
            if prev_was_text:
                text_segmented[-1] = ("text", text_segmented[-1][1] + "\n" + tag.getText())
            else:
                text_segmented.append(("text",tag.getText()))

            prev_was_text = True

    contents_dict["text_segmented"] = text_segmented
    outname = contents_dict["title"].replace(" ","_").replace(":","")
    write_files(contents_dict,write_path,outname,"pickle")
    #return contents_dict
