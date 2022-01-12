# text-matcher

[![PyPI version](https://badge.fury.io/py/text-matcher.svg)](https://badge.fury.io/py/text-matcher)
[![DOI](https://zenodo.org/badge/70358326.svg)](https://zenodo.org/badge/latestdoi/70358326)

A simple text reuse detection CLI tool. Given a pair of texts or directories of texts, it will find similar text between them. This is good for detection of text reuses such as citation, quotation, intertextuality, and plagiarism. 

The pilot experiment that uses this tool is [allusion-detection](https://github.com/JonathanReeve/allusion-detection). A new project that uses this tool is [middlemarch-critical-histories](https://github.com/xpmethod/middlemarch-critical-histories). 

# Demo

Does Milton quote from the Bible in his _Areopagitica_? Let’s find out.

```
$ text-matcher kjv.txt areopagitica.txt 

1 total matches found.

match 1:
kjv.txt: (4135539, 4135561) Spirit. 5:20 Despise not prophesyings Prove all things; hold fast that which is good. 5:22 Abstain
areopagitica.txt: (25861, 25883) answerable to that of the Apostle to the Thessalonians PROVE ALL THINGS, HOLD FAST THAT WHICH IS GOOD. And he might
```

# Usage

Just run `text-matcher` and provide the names of the text files you want to compare. You can also provide a directory of files instead of a single file, so if you want to compare `textA.txt` with every text file in `textdir/`, run `text-matcher textA.txt textdir/`. 

You can also tweak the matching by providing the ngrams value to match against, and the threshold. From the help: 

```
$ text-matcher --help
Usage: text-matcher [OPTIONS] TEXT1 TEXT2

  This program finds similar text in two text files.

Options:
  -t, --threshold INTEGER    The shortest length of match to include in the
                             list of initial matches.
  -c, --cutoff INTEGER       The shortest length of match to include in the
                             final list of extended matches.
  -n, --ngrams INTEGER       The ngram n-value to match against.
  -m, --mindistance INTEGER  The minimum value for distance between two
                             match.
  -l, --logfile TEXT         The name of the log file to write to.
  --stops                    Include stopwords in matching.
  --verbose                  Enable verbose mode, giving more information.
  --help                     Show this message and exit.
```

# Installation

You can install `text-matcher` using `pip`: 

``` sh
pip3 install --user text-matcher
```

Or globally, with `sudo`: 

```sh
sudo pip3 install text-matcher
```

Alternatively, clone this repo and install locally, using pip: 

```
git clone https://github.com/JonathanReeve/text-matcher
cd text-matcher
pip install .
```

Or with Pipenv: 

```
git clone https://github.com/JonathanReeve/text-matcher
cd text-matcher
pipenv install .
pipenv run text-matcher
```

# Citation

If you use `text-matcher` in your research, you can cite it like this, for now: 

```
@misc{Reeve2020,
  author = {Reeve, Jonathan},
  title = {Text-Matcher},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/JonathanReeve/text-matcher}},
  commit = {988d9422a63165225ea136fc31427b1e57814505},
  doi = {10.5281/zenodo.3937738}
}
```

