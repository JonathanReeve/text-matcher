# text-matcher
A simple text reuse detection CLI tool.

The experiment that this grew out from is now at https://github.com/JonathanReeve/allusion-detection. Another project that uses this tool is https://github.com/xpmethod/middlemarch-critical-histories. 

# Usage

Just run `text-matcher` and provide the names of the text files you want to compare. You can also provide a directory of files instead of a single file, so if you want to compare `textA.txt` with every text file in `textdir/`, run `text-matcher textA.txt textdir/`. 

You can also tweak the matching by providing the ngrams value to match against, and the threshold. From the help: 

```
$ text-matcher --help
Usage: text-matcher [OPTIONS] TEXT1 TEXT2

  This program finds similar text in two text files.

Options:
  -t, --threshold INTEGER  The shortest length of match to include.
  -n, --ngrams INTEGER     The ngram n-value to match against.
  -l, --logfile TEXT       The name of the log file to write to.
  --verbose                Whether to enable verbose mode, giving more
                           information.
  --help                   Show this message and exit.
```

# Installation

You can install `text-matcher` using `pip`: 

On Arch or a modern Linux distribution that uses python3, run: `pip install text-matcher`. 

On Ubuntu or a similar distribution that uses an old version of Python, run: `sudo pip3 install text-matcher`. 

Alternatively, clone this repo and install using pip: 

```
git clone https://github.com/JonathanReeve/text-matcher
pip install .
```
