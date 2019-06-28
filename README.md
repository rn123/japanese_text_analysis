Japanese Text Analysis Experiments
==============================

This is a set of experiments to examine word usage trends in Japanese texts.

Environment
------------
Primarily, use a conda environment to track packages and requirements needed to reproduce experiments. 
Use jupyter lab for bulk of experiments as well as Plotly Dash for visualizations and command line scripts
for building models and pulling data.

Create the conda environment via command line:
```
make create_environment
source activate japanese_text_analysis
```

Should now be able to run Jupyer Lab:
```
jupyter lab --notebook-dir=notebooks
```

Data
----

Primary sources of Japanese textual data for experiments:

* The text for the "Tale of Genji": [Japanese Text Initiative](http://jti.lib.virginia.edu/japanese/genji/) from the University of Virgninia.
* Images for scroll: [Genji](http://codh.rois.ac.jp/pmjt/book/200014735/200014735.zip).
* [Blog](https://scholarblogs.emory.edu/japanese-text-mining/) and data for Japanese Text Minining.

Pull datasets with command line:
```
make data
```

For the background language model, the script downloads the [precomputed fasttext word vectors](https://fasttext.cc/docs/en/crawl-vectors.html) and converts them to [`pymagnitude`](https://github.com/plasticityai/magnitude) format. 
```
make background
```

Experiments
-----------

1. Scrape and clean (modern) Japanese text for [源氏物語歌合絵巻](https://github.com/rn123/japanese_text_analysis/blob/master/notebooks/RN%201.0%20Genji%20Data.ipynb).
2. [Extracting and clustering significant terms.](https://github.com/rn123/japanese_text_analysis/blob/master/notebooks/RN%201.0%20Genji%20Clustering%20Significant%20Terms.ipynb)
3. [Dunning's likelihood ratio test comparing text to background corpus.](https://github.com/rn123/japanese_text_analysis/blob/master/notebooks/Statistics%20of%20Surprise%20and%20Coincidence.ipynb)
4. English fiction example, [The Hobbit.](https://github.com/rn123/japanese_text_analysis/blob/master/notebooks/textual_analysis_hobbit.ipynb)

References
----------

“Genji Monogatari.” Accessed June 28, 2019. http://jti.lib.virginia.edu/japanese/genji/.

“Japanese Text Mining – Emory University | ECDS | QuanTM | May 30th – June 2nd, 2017.” Accessed June 28, 2019. https://scholarblogs.emory.edu/japanese-text-mining/.

“源氏物語歌合絵巻 | 日本古典籍データセット - ROIS-DS人文学オープンデータ共同利用センター(CODH).” 人文学オープンデータ共同利用センター(CODH). Accessed June 28, 2019. http://codh.rois.ac.jp/pmjt/book/200014735/.

Ortuño, M, P Carpena, P Bernaola-Galván, E Muñoz, and A. M Somoza. “Keyword Detection in Natural Languages and DNA.” Europhysics Letters (EPL) 57, no. 5 (March 2002): 759–64. https://doi.org/10.1209/epl/i2002-00528-3.

“Word Vectors for 157 Languages · FastText.” Accessed June 28, 2019. https://fasttext.cc/index.html.

A Fast, Efficient Universal Vector Embedding Utility Package.: Plasticityai/Magnitude. Python. 2018. Reprint, Plasticity, 2019. https://github.com/plasticityai/magnitude.

Dunning, Ted. A Python Implementation of the Most Commonly Used Variants of the G-Test: Tdunning/Python-Llr. Python, 2019. https://github.com/tdunning/python-llr.

Dunning, Ted. “Finding Structure in Text, Genome and Other Symbolic Sequences.” ArXiv:1207.1847 [Cs], July 8, 2012. http://arxiv.org/abs/1207.1847.


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
