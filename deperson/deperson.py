# (c) KPN B.V. 
# Licensed under MIT License (see LICENSE.txt)
# Author: Marco Tompitak, Text Analytics Group, KPN Data Science Lab

import codecs
import difflib
import os
import re
import string
import csv

from hunspell import HunSpell
from unidecode import unidecode

PLACEHOLDER = '@#$!'

# Current directory
script_path = os.path.dirname(os.path.realpath(__file__))


class Deperson():

    def __init__(self, autocorrect=False, check_compound=False):
        self.autocorrect = autocorrect
        self.check_compound = check_compound

        self.masking_regexes = [
            (r'(?:van|aan|in)\s(?:der|den)\s\b\w+\b', 3),
            (re.escape(PLACEHOLDER) +
                r'\s(?:van|aan|in)\s(?:de|het|t)\s\b\w+\b', 4)
        ]

        self.email_regex = r'[^@\s]+@[^@\s]+\.[^@\s]+'

        self.email_placeholder = 'maskedemail'

        self.url_regex = r'(?:http:\/\/|https:\/\/)?(?:www\.)?[a-z]+\.[a-z]{2,5}[^\s]*'

        # Import blacklists
        blacklists_path = script_path + '/blacklists/'
        blacklists = []

        # Loop over available blacklists
        for filename in os.listdir(blacklists_path):
            if filename.endswith(".txt"):
                # Open assuming we may be dealing with unicode
                with codecs.open(
                        blacklists_path + filename, encoding='utf-8') as f:
                    # Decode unicode into ASCII
                    words = {unidecode(x.strip()) for x in f.readlines()}
                # Store current blacklist
                blacklists.append(words)
            else:
                continue

        # Combine all blacklists into one
        self.blacklist = set.union(*blacklists)

        # Regex-based whitelists
        self.whitelist_regexes = [
            r'\d+gb$',
            r'\d+ghz$',
            r'\d+mb$',
            r'\d+mbit$',
            r'\d+gbit$',
            r'\d+(?:\.|,)?\d{0,2}euro?',
            r'v\d+$',
            r'0(?:8|9)00(?:[\s\-]{1}\d{4})?',
            u'\u20AC\d+(?:\.|,)?\d{0,2}',
            r'^\d$',
            r'^[a-zA-Z]{1,2}\d{1,3}$',
            r'\d{1,2}:\d{2}(?::\d{2})?',
            r'\d{1,2}-\d{1,2}(?:-\d{2,4})?'
        ] + [self.url_regex]

        self.protected_punctuation_regexes = [
            r'0(?:8|9)00[\s\-]{1}\d{4}',
            u'\u20AC\d+(?:\.|,)?\d{0,2}',
        ] + [
            self.url_regex,
            self.email_regex
        ] + self.whitelist_regexes

        self.protected_punctuation_regex = '(' + \
            '|'.join(self.protected_punctuation_regexes) + ')'

        # Load in HunSpell files
        self.d = HunSpell(script_path + '/dict/Dutch.dic',
                          script_path + '/dict/Dutch.aff')

        self.clean_d = HunSpell(script_path + '/dict/Dutch_clean.dic',
                                script_path + '/dict/Dutch.aff')

        # Load in curated autocorrection list
        with open(script_path + '/spellcheck/autocorrect.csv') as f:
            reader = csv.reader(f, skipinitialspace=True)
            self.autocorrecter = dict(reader)

        # Import whitelists
        whitelists_path = script_path + '/whitelists/'
        whitelists = []

        # Loop over available whitelists
        for filename in os.listdir(whitelists_path):
            if filename.endswith(".txt"):
                # Open assuming we may be dealing with unicode
                with codecs.open(
                        whitelists_path + filename, encoding='utf-8') as f:
                    # Decode unicode into ASCII
                    words = {unidecode(x.strip()) for x in f.readlines()}
                # Store current whitelist
                whitelists.append(words)
            else:
                continue

        # Combine all whitelists into one
        self.whitelist = set.union(*whitelists)
        self.whitelist = self.whitelist.union(set(self.autocorrecter.keys()))

        # Specific domain words whitelist
        with codecs.open(
                whitelists_path + 'domainwords.txt', encoding='utf-8') as f:
            self.domain_whitelist = {
                unidecode(x.strip()) for x in f.readlines()}

    def curated_autocorrect(self, word):
        """
            Autocorrect a word based on the curated list of autocorrection
            sets.
        """

        if word in self.autocorrecter:
            corr = self.autocorrecter[word]
        else:
            return word

        return corr

    def smart_suggest(self, word):
        """
            Autocorrect a word. (This is computationally expensive,
            use sparingly.)

            Keyword arguments:
            word -- a (potentially misspelled) Dutch word

            Return value:
            Corrected word or, if no suggestion could be found,
            the original word.
        """

        if word.isdigit():
            return word

        # Set of all suggestions provided by HunSpell for this word;
        # insensitive to the capitalization of the first letter
        suggestions = set(self.d.suggest(word)).union(
            set(self.d.suggest(word.capitalize())))

        # If we have no suggestions, just return the word
        if(len(suggestions) == 0):
            return word

        # Otherwise, we want to return the closest match, where 'closest' is
        # defined by the Ratcliff/Obershelp pattern matching algorithm.
        worset, max = {}, 0
        for sugg in suggestions:
            # Create a temporary SequenceMatcher instance (provides the
            # matching algorithm) that operates case-insensitively
            tmp = difflib.SequenceMatcher(
                None,
                word.lower(),
                sugg.lower(),
                autojunk=False
            ).ratio()

            # Store the suggestion with its score
            worset[tmp] = sugg

            # Keep track of the suggestion with max score
            if tmp > max:
                max = tmp

        # Return best match (case insensitive)
        return worset[max].lower()

    def remove_punctuation(self, s):
        """
            Drop punctuation from a string
        """

        # Punctuation but not the '|' character
        punct = string.punctuation.replace(
            "|", "").replace("[", "").replace("]", "")

        # Translator that maps punctuation to spaces
        translator = str.maketrans(punct, ' ' * len(punct))

        # Split out protected patterns to preserve them
        split = re.split(self.protected_punctuation_regex, s)

        # print(split)

        # Remove punctuation from even-index parts of the split
        cleaned_split = [
            part.translate(translator)
            if i % 2 == 0
            else part
            for i, part in enumerate(split)
        ]

        # Put string back together
        t = ''.join(cleaned_split)

        # Mask out e-mail addresses
        t = re.sub(self.email_regex, self.email_placeholder, t)

        # Translated string
        # t = s.translate(translator)

        # Remove duplicate whitespaces
        # t = ' '.join(t.split())

        return t

    def apply_whitelist(self, text):
        """
            Filter text using whitelist
        """

        # Split text into words
        words = self.remove_punctuation(text.lower()).split()

        # Correct text based on curated autocorrecter
        if self.autocorrect:
            for word in words:
                if word in self.autocorrecter:
                    idx = words.index(word)

                    # Replacement may consist of more than one word, so insert
                    # as a list
                    words[idx:idx + 1] = self.curated_autocorrect(word).split()

        # Calculate filter based on whitelist(TODO paralellize?)
        filter = list(map(lambda word: (word, word in self.whitelist), words))

        # Update filter based on whitelist regexes
        filter = [
            (word, f)
            if f
            else (word,
                  any(
                      re.match(regex, word)
                      for regex in self.whitelist_regexes
                  ))
            for (word, f) in filter
        ]

        # Update filter based on compound words
        if self.check_compound:
            for i in range(len(filter)):
                (word, f) = filter[i]
                if f or word.isdigit():
                    continue
                else:
                    if self.clean_d.spell(word):
                        filter[i] = (word, True)

        # Update filter based on autocorrection
        # # This is currently too slow, do not use
        # if self.autocorrect:
        #     for i in range(len(filter)):
        #         (word, f) = filter[i]
        #         if f or word.isdigit():
        #             continue
        #         else:
        #             corr = self.smart_suggest(word)
        #             if corr in self.whitelist:
        #                 filter[i] = (corr, True)

        # Put text back together without filtered words
        return ' '.join([
            word
            if f
            # or (self.check_compound and self.d.spell(word))
            # or (self.autocorrect and self.smart_suggest(word) in
            # self.whitelist)
            else PLACEHOLDER
            for (word, f) in filter
        ])

    def domain_guarded_replace(self, regex, text, repl):
        """
            Replace based on regex, but guarding domain-specific words.
        """

        # Loop over matches for regex
        for match in re.finditer(regex, text):
            # Pull out the matched substring
            g = match.group()

            # Replace it with placeholder only if none of the words in the
            # substring are in the domain whitelist
            if not any(word in self.domain_whitelist for word in g.split()):
                text = text.replace(g, repl)
        return text

    def apply_blacklist(self, text):
        """
            Apply all defined regex masks and the blacklist
        """

        # Copy text
        output = text[:]

        # Mask out blacklisted strings
        for bad_word in self.blacklist:
            num_ph = len(bad_word.split())
            multi_ph = (PLACEHOLDER,) * num_ph
            repl = ' '.join(multi_ph)
            output = output.replace(bad_word, repl)

        # Mask out based on regexes
        for (regex, num_ph) in self.masking_regexes:
            multi_ph = (PLACEHOLDER,) * num_ph
            repl = ' '.join(multi_ph)
            output = self.domain_guarded_replace(regex, output, repl)

        return output

    def get_illegal_words(self, text):
        """
            Return words masked by apply_whitelist() from the
            given text.
        """

        # Get masked words
        cleaned = self.apply_blacklist(self.apply_whitelist(text)).split()

        # Original text
        original = self.remove_punctuation(text).split()

        # Pull out original words that were filtered out
        filtered = [original[i]
                    for i in range(len(original))
                    if cleaned[i] == PLACEHOLDER]

        # Return as string
        return ' '.join(filtered)
