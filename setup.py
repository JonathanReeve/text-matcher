from distutils.core import setup
from sys import version_info as ver

if ver[0] < 3:
    version = str(ver[0]) + '.' + str(ver[1])
    sys.exit("""
    Error: your Python version is %s, but text-matcher requires at least
    Python 3. Please upgrade your Python installation, or try using pip3
    instead of pip.""" % version)

setup(
    name = 'text-matcher',
    packages = ['text_matcher'], 
    version = '0.1.3',
    description = 'A simple text reuse detection CLI tool.',
    author = 'Jonathan Reeve',
    author_email = 'jon.reeve@gmail.com',
    url = 'https://github.com/JonathanReeve/text-matcher', 
    download_url = 'https://github.com/JonathanReeve/text-matcher/tarball/0.1.3', 
    install_requires = ['Click', 'nltk', 'termcolor'],
    keywords = ['NLP', 'text', 'text reuse'],
    entry_points='''
    [console_scripts]
    text-matcher = text_matcher.text_matcher:cli''',
)
