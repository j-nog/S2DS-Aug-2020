# Nationbetter package

The nationbetter package was written by the combined efforts of
Eyzo Stouten @EyzoStouten - PDF scraping and package management
Bernhard Mitterwallner - HTML scraping
Ercan Pilicer - PDF scraping and NLP implementation
Hanna Sjoerberg - NLP implementation
Joao Nogueira - NLP implementation
Neri van Otten - Project manager
During the Pivigo S2DS London Virtual August, as commissioned by Nation better (
https://nationbetter.uk).

The intention of this package is to function as a proof of concept to explore 
whether it is possible to automatically download, read and interpret the corpus
of legal documents regarding sponsorship and legal applicant guidance for Tier 2
 - 5 visa applications. The package attempts to download a given set of pdf
document and extract their contents as well as extract the contents of online
html guides given a set of urls provided in the "pdf\_urls.txt and "urls.txt" 
files provided with the package. These documents are automatically partitioned
into sections which TODO: will be labeled by a given OR extracted set. Using
these labels the corpus can be parsed for the relevant sections given a 
particular set of labels.

## Features
* Downloads pdfs to local folder ~/S2SS/NationBetter/data given a set of urls.
* Extracts raw contents of pdfs and html documents into dataframes TODO:(and
stores them?).
* Raw contents are partitioned into (sub) sections, labeled by text type and 
location in the text and TODO:(stored?) as DataFrames.
* Text is labeled by a set of relevant keys 
* TODO: FINISH

## How to use
* Install python 3.6 or newer
* Install the package
```
pip install [path of package]
```
* Install dependencies (if necessary)
```
pip install -r [path of package]/requirements.txt
```
* Try out the demo provided with the package at
```
python [path of package]/examples/[any of the examples].py
```
* For development purposes, just run the example\_build\_data.py to build
the full tree containing the raw and cleaned data.
* For testing purposes all dataframes are stored and can be opened as shown in
example\_retrieve\_dataframes.py 
* When providing urls for reading preferably do so in files that come with the
package: urls.txt and pdf\_urls.txt. However the .read\_text([path]) function 
takes arbitrary paths as an argument.
* When changing the urls make sure to put them as http...... on separate lines
to evade errors.

## How to use with venv
* Create the venv using 
```
python3 -m venv venv
```
or 
```
python3 -m venv [relative path to nationbetter/]venv
```
Please use the venv name, it was already excluded 
in the .gitignore file!
* Activate venv using 
```
source venv/bin/activate
```
* install requirements with 
```
pip install -r requirements.txt 
```
* Install the package
```
pip install [path of package]
```
* Run the code.

## To update
* If updates are pushed and they are not working, consider running
```
pip install NationBeter-PIVIGO-GovUKCorpusParser --upgrade
```
* Or use the absolute path
```
pip install [path to nationbetter] --upgrade
```
