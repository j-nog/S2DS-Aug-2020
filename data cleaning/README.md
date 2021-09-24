# How does the data cleaning pipeline work?


### Scrape all the "Immigration Rules" documents from https://www.gov.uk/guidance/immigration-rules
The the script `scrape_immigration_rules.py` scrapes all the linked documents (about 50) and
pickles the resulting data frame into `immigration_rules_scrape.pickle`. 
The script can also be run from within a Jupyter notebook as demonstrated in
`scrape_immigration_rules.ipynb`.


### What is the format of the segmented text?
The HTML scraper returns a list of that holds the text segments in the order in which they appear in the text.
Each element of that list is a tuple of the form `(label,string)`, where `label` can be "section","subsection","table","text"
and `string` is the corresponding string of the text element.

_I know that this might not be perfect. We should do some brainstorming and then agree on a format_

Such a list of segmented text can be turned into a data frame with
the function `build_segments_df(segments)` in `text_wrangling_utils.py`

### I just want to scrape a gov.uk/guidance HTML document. What do I do?
The `scrape_govuk_guidance` in `web_scraping_lib.py ` does that.
