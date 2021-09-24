[![N|Solid](./static/logo.jpg)](https://nationbetter.uk/)

## Application Interface
This is a summary documentation for how to run the interface which displays sections and subsections extracted from whole legal documents.

### File Information
[app.py](https://github.com/S2DSLondon/Aug20_NationBetter/tree/master/deliverable/interface/app.py) script utilizes two python files:
* [keywords.py](../package_nationbetter/nationbetter/keywords.py) is used to populated dropdown lists.
* [tfidf_search.py](https://github.com/S2DSLondon/Aug20_NationBetter/blob/master/NLP/keywords_demo/tfidf_search.py) is used to apply **search_corpus_tfidf** function.

---
> **_Attention:_** In order to run the interface, you need to have pickled data which contains the information from **whole legal documents (PDFs and HTMLs)**. To produce the pickled data you can run [adding_keywords.ipynb](../notebooks_docs/adding_keywords.ipynb) notebook file.
---

The pickled data will be located under **data_nationbetter** folder.

### Required Packages

As long as you installed [nationbetter](https://github.com/S2DSLondon/Aug20_NationBetter/tree/master/deliverable/package_nationbetter) package everything should be fine. Otherwise, you may need to have these packages.

```sh
$ cd application_folder
$ pip install flask pandas flashtext
```

### How to Run

Once you installed [nationbetter](https://github.com/S2DSLondon/Aug20_NationBetter/tree/master/deliverable/package_nationbetter), you can open a **terminal** in order to run **Python**, and then the application interface.

You should go to the application interface folder and call the `app.py` script.

```sh
$ cd application_folder
$ python app.py
```
Once it is done, you can open any browser and paste the given port number (e.g. `http://127.0.0.1:5000/`)
