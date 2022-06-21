# coding: utf-8

import re
import os
import json
import logging
import itertools
import nltk
from difflib import SequenceMatcher
from nltk.metrics.distance import edit_distance as editDistance
from nltk.stem.lancaster import LancasterStemmer
from nltk.util import ngrams
from string import punctuation
from termcolor import colored


class Text:
    def __init__(self, raw_text, label, removeStopwords=True):
        if type(raw_text) == list:
            # JSTOR critical works come in lists, where each item represents a page.
            self.text = ' \n '.join(raw_text)
        else:
            self.text = raw_text
        self.label = label
        self.preprocess(self.text)
        self.tokens = self.getTokens(removeStopwords)
        self.trigrams = self.ngrams(3)

    def preprocess(self, text):
        """ Heals hyphenated words, and maybe other things. """
        self.text = re.sub(r'([A-Za-z])- ([a-z])', r'\1\2', self.text)

    def getTokens(self, removeStopwords=True):
        """ Tokenizes the text, breaking it up into words, removing punctuation. """
        tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*')  # A custom regex tokenizer.
        spans = list(tokenizer.span_tokenize(self.text))
        # Take note of how many spans there are in the text
        self.length = spans[-1][-1]
        tokens = tokenizer.tokenize(self.text)
        tokens = [token.lower() for token in tokens]  # make them lowercase
        stemmer = LancasterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        if not removeStopwords:
            self.spans = spans
            return tokens
        tokenSpans = list(zip(tokens, spans))  # zip it up
        stopwords = nltk.corpus.stopwords.words('english')  # get stopwords
        tokenSpans = [token for token in tokenSpans if token[0] not in stopwords]  # remove stopwords from zip
        self.spans = [x[1] for x in tokenSpans]  # unzip; get spans
        return [x[0] for x in tokenSpans]  # unzip; get tokens

    def ngrams(self, n):
        """ Returns ngrams for the text."""
        return list(ngrams(self.tokens, n))


class ExtendedMatch:
    """
    Data structure container for a fancy version of a difflib-style
    Match object. The difflib Match class won't work for extended
    matches, since it only has the properties `a` (start location in
    text A), `b` (start location in text B), and size. Since our fancy
    new matches have different sizes in our different texts, we'll need
    two size attributes.
    """

    def __init__(self, a, b, sizeA, sizeB):
        self.a = a
        self.b = b
        self.sizeA = sizeA
        self.sizeB = sizeB
        # Whether this is actually two matches that have been fused into one.
        self.healed = False
        # Whether this match has been extended from its original boundaries.
        self.extendedBackwards = 0
        self.extendedForwards = 0

    def __repr__(self):
        out = "a: %s, b: %s, size a: %s, size b: %s" % (self.a, self.b, self.sizeA, self.sizeB)
        if self.extendedBackwards:
            out += ", extended backwards x%s" % self.extendedBackwards
        if self.extendedForwards:
            out += ", extended forwards x%s" % self.extendedForwards
        if self.healed:
            out += ", healed"
        return out


class Matcher:
    """
    Does the text matching.
    """

    def __init__(self, textObjA, textObjB, threshold=3, cutoff=5, ngramSize=3, removeStopwords=True, minDistance=8, silent=False):

        """
        Takes as input two Text() objects, and matches between them.
        """
        self.threshold = threshold
        self.ngramSize = ngramSize
        self.minDistance = minDistance

        self.textA = textObjA
        self.textB = textObjB

        self.textAgrams = self.textA.ngrams(ngramSize)
        self.textBgrams = self.textB.ngrams(ngramSize)

        self.locationsA = []
        self.locationsB = []

        self.initial_matches = self.get_initial_matches()
        self.healed_matches = self.heal_neighboring_matches()

        # Rewrote just after
        self.extended_matches = self.extend_matches()

        # Prune matches
        self.extended_matches = [match for match in self.extended_matches
                                 if min(match.sizeA, match.sizeB) >= cutoff]

        self.numMatches = len(self.extended_matches)

        self.silent = silent

    def get_initial_matches(self):
        """
        This does the main work of finding matching n-gram sequences between
        the texts.
        """
        sequence = SequenceMatcher(None, self.textAgrams, self.textBgrams)
        matchingBlocks = sequence.get_matching_blocks()

        # Only return the matching sequences that are higher than the
        # threshold given by the user.
        highMatchingBlocks = [match for match in matchingBlocks if match.size > self.threshold]

        numBlocks = len(highMatchingBlocks)

        if numBlocks > 0 and self.silent is not True:
            print('%s total matches found.' % numBlocks, flush=True)

        return highMatchingBlocks

    def getContext(self, text, start, length, context):
        match = self.getTokensText(text, start, length)
        before = self.getTokensText(text, start - context, context)
        after = self.getTokensText(text, start + length, context)
        match = colored(match, 'red')
        out = " ".join([before, match, after])
        out = out.replace('\n', ' ')  # Replace newlines with spaces.
        out = re.sub('\s+', ' ', out)
        return out

    def getTokensText(self, text, start, length):
        """ Looks up the passage in the original text, using its spans. """
        matchTokens = text.tokens[start:start + length]
        spans = text.spans[start:start + length]
        if len(spans) == 0:
            # Don't try to get text or context beyond the end of a text.
            passage = ""
        else:
            passage = text.text[spans[0][0]:spans[-1][-1]]
        return passage

    def getLocations(self, text, start, length, asPercentages=False):
        """ Gets the numeric locations of the match. """
        spans = text.spans[start:start + length]
        if asPercentages:
            locations = (spans[0][0] / text.length, spans[-1][-1] / text.length)
        else:
            try:
                locations = (spans[0][0], spans[-1][-1])
            except IndexError:
                return None
        return locations

    def getMatch(self, match, context=5):
        textA, textB = self.textA, self.textB
        lengthA = match.sizeA + self.ngramSize - 1  # offset according to nGram size
        lengthB = match.sizeB + self.ngramSize - 1  # offset according to nGram size
        wordsA = self.getContext(textA, match.a, lengthA, context)
        wordsB = self.getContext(textB, match.b, lengthB, context)
        spansA = self.getLocations(textA, match.a, lengthA)
        spansB = self.getLocations(textB, match.b, lengthB)
        if spansA is not None and spansB is not None:
            self.locationsA.append(spansA)
            self.locationsB.append(spansB)
            line1 = ('%s: %s %s' % (colored(textA.label, 'green'), spansA, wordsA))
            line2 = ('%s: %s %s' % (colored(textB.label, 'green'), spansB, wordsB))
            out = line1 + '\n' + line2
            return out

    def heal_neighboring_matches(self):
        healedMatches = []
        ignoreNext = False
        matches = self.initial_matches.copy()
        # Handle only one match.
        if len(matches) == 1:
            match = matches[0]
            sizeA, sizeB = match.size, match.size
            match = ExtendedMatch(match.a, match.b, sizeA, sizeB)
            healedMatches.append(match)
            return healedMatches
        # For multiple match
        for i, match in enumerate(matches):
            # If last match
            if i + 1 > len(matches) - 1:
                break
            nextMatch = matches[i + 1]
            # If math already treated
            if ignoreNext:
                ignoreNext = False
                continue
            else:
                # Look at the number of different character between two raw match
                if (nextMatch.a - (match.a + match.size)) < self.minDistance:
                    # logging.debug('Potential healing candidate found: ' % (match, nextMatch))
                    sizeA = (nextMatch.a + nextMatch.size) - match.a
                    sizeB = (nextMatch.b + nextMatch.size) - match.b
                    healed = ExtendedMatch(match.a, match.b, sizeA, sizeB)
                    healed.healed = True
                    healedMatches.append(healed)
                    ignoreNext = True
                else:
                    sizeA, sizeB = match.size, match.size
                    match = ExtendedMatch(match.a, match.b, sizeA, sizeB)
                    healedMatches.append(match)
        return healedMatches

    def edit_ratio(self, wordA, wordB):
        """ Computes the number of edits required to transform one
        (stemmed already, probably) word into another word, and
        adjusts for the average number of letters in each.

        Examples:
        color, colour: 0.1818181818
        theater, theatre: 0.2857
        day, today: 0.5
        foobar, foo56bar: 0.2857
        """
        distance = editDistance(wordA, wordB)
        averageLength = (len(wordA) + len(wordB)) / 2
        return distance / averageLength

    def extend_matches(self, cutoff=0.4):
        extended = False
        for match in self.healed_matches:
            # Look one word before.
            wordA = self.textAgrams[(match.a - 1)][0]
            wordB = self.textBgrams[(match.b - 1)][0]
            if self.edit_ratio(wordA, wordB) < cutoff:
                if self.silent is not True:
                    print('Extending match backwards with words: %s %s' %
                        (wordA, wordB))
                match.a -= 1
                match.b -= 1
                match.sizeA += 1
                match.sizeB += 1
                match.extendedBackwards += 1
                extended = True
            # Look one word after.
            idxA = match.a + match.sizeA + 1
            idxB = match.b + match.sizeB + 1
            if idxA > len(self.textAgrams) - 1 or idxB > len(self.textBgrams) - 1:
                # We've gone too far, and we're actually at the end of the text.
                continue
            wordA = self.textAgrams[idxA][-1]
            wordB = self.textBgrams[idxB][-1]
            if self.edit_ratio(wordA, wordB) < cutoff:
                if self.silent is not True:
                    print('Extending match forwards with words: %s %s' %
                        (wordA, wordB))
                match.sizeA += 1
                match.sizeB += 1
                match.extendedForwards += 1
                extended = True

        if extended:
            # If we've gone through the whole list and there's nothing
            # left to extend, then stop. Otherwise do this again.
            self.extend_matches()

        return self.healed_matches

    def match(self):
        """ Gets and prints all matches. """

        for num, match in enumerate(self.extended_matches):
            # print('match: ', match)
            out = self.getMatch(match)
            if self.silent is not True:
                print('\n')
                print('match %s:' % (num + 1), flush=True)
                print(out, flush=True)

        return self.numMatches, self.locationsA, self.locationsB
