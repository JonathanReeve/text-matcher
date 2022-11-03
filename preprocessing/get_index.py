import re
import sys


def getCharIndex(textfile, quote):
    '''
    Returns the spans of the quote in the textfile.
    '''
    # Get the text of the textfile
    with open(textfile, 'r') as f:
        text = f.read()
    # Get the spans of the quote in the text
    spans = []
    for match in re.finditer(quote, text):
        spans.append(match.span())
    return spans


if __name__ == "__main__":
    a = sys.argv[1]
    b = sys.argv[2]
    print(getCharIndex(a, b))
