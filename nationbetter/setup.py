import setuptools

with open("README.md", "r") as fh:
    long_description=fh.read()

setuptools.setup(
        name="NationBeter-PIVIGO-GovUKCorpusParser",
        version="0.0.1",
        author="Eyzo Stouten",
        email="emstouten@gmail.com",
        description="""Package for reading and indexing a corpus of legal 
                        documentd from the gov.uk website regardig visa 
                        application processes.
                        """,
        long_description=long_description,        
        long_description_content_type="text/markdown",
        url="https://github.com/S2DSLondon/Aug20_NationBetter/tree/master/nationbetter",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT Licence",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6'
)

