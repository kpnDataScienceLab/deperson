_deperson_ - depersonalization package for Dutch text
----

This python package aims to remove sensitive data from Dutch texts. Such data includes:
 - Names of persons and places
 - Street names and house numbers
 - Postal codes
 - Phone numbers
 - Bank account numbers
 - Dates (e.g. of birth)

## Whitelisting vs Blacklisting

This package represents the second iteration in the effort to depersonalize text. The first version relied on blacklisting common first and last names and all numbers.

Such blacklists are inevitably not exhaustive, and tended to let uncommon names and names with alternative spellings through. Obtaining clean blacklists, i.e. lists that did not mask too much, also turned out to be a challenge.

A safer approch to depersonalization is to whitelist all parts of text that are considered non-sensitive. This way, anything not explicitly approved is assumed to be sensitive information; e.g. a name will be blocked no matter its specific spelling.

Whitelisting as a methodology has its own caveats, not the least of which is the required comprehensive dictionary of valid words to whitelist.

## The Dutch whitelist

The whitelist used in this packaged is constructed from the [Dutch dictionary and affix files for HunSpell](https://github.com/titoBouzout/Dictionaries), an open-source spellchecker. (These files are available under the BSD and CC Attribution 3.0 Unported licenses, see LICENSE.txt in deperson/dict/.)

The dictionary definitions consist of a list of basic words together with a number of flags (e.g. `Dutch.dic`) defining how those words can be modified or composed to generate new words or wordforms. A second file (`Dutch.aff`) defines the meaning of the flags.

Hunspell itself [provides functionality](https://github.com/hunspell/hunspell/tree/master/src/tools) to decompile these files into lists of words in all their forms.

For building a whitelist suitable for depersonalization, the dictionary was culled by removing all proper names (flag `PN`), before generating word forms.

## Compound words

In the Dutch language, words can be composed indefinitely to create new words. In theory, there is an infinite number of Dutch words. When generating wordforms, these compound words are not generated, and are therefore not part of the whitelist.

To allow such compound words, any words that are not found in the whitelist can be (optionally) run through the spellchecker itself, through the `hunspell` wrapper in Python. (See Basic Usage below.) This process is limited to words that are not already validated (or invalidated) through other means (such as the whitelist) for performance reasons.

## Further whitelists

Besides a comprehensive list of Dutch words, we may want to whitelist additional words that are domain-specific or application-specific. For instance, for interactions with KPN customers it makes sense to whitelist non-dictionary terms such as 'kpn', 'apple', or 'spotify'. When dealing with chats, it can help to whitelist (or autocorrect, see below) commonly used slang or shorthand.

For these purposes, additional (curated) whitelists are included, and can be added.

## Autocorrection

When dealing with user-typed text data such as chat transcripts, spelling mistakes are inevitable. Since misspelled words are not in the dictionary, they will be masked unless the spelling is corrected.

For the purposes of depersonalization, general autocorrection is dangerous, because it may autocorrect sensitive information in such a way that the information remains readable to a human.

This package therefore opts for curated (and optional) autocorrection. It provides a basic list of misspellings, and their correctly-spelled forms. It is advisable to augment it with domain-specific common misspellings.

## Basic usage

#### Installation requirements
Your python environment should contain the following packages, to be installed with pip:

* unidecode
* hunspell

In order to import hunspell and having it work in Ubuntu you need first to install hunspell dev libraries:
```
sudo apt-get update
sudo apt-get install libhunspell-dev
```

#### The `Deperson` class

The package currently exposes just a single class `deperson.Deperson`, which defines the depersonalizer object. Example usage would be

```python
from deperson.deperson import Deperson
d = Deperson(autocorrect=True, check_compound=True)
print(d.apply_blacklist(d.apply_whitelist('Mijn naam is Peter')))
```
Output:
`mijn naam is @#$!`

The class initializer takes two boolean values (default `False`) to switch on autocorrection (as described above) and checking with the spellchecker for compound words.

The package is designed such that both these optional functions are only applied when necessary, leading to a manageable increase in computational cost, and it is recommended to turn them on.

#### Packaged scripts

The package installs two (sample) scripts that utilize the Deperson class to operate on pickled `pandas` dataframes:
 - `deperson_pickle.py`runs over the records in a (user-specified) column of the dataframe and applies depersonalization, creating a new column and outputting the resulting dataframe to another pickle file.
 - `illegal_words_from_pickle.py` does much the same but rather than depersonalizing the text, it simply collects all the words that would be masked out by applying depersonalization.

## Caveats

#### Names that are also dictionary words

Although whitelisting is safer than blacklisting, some caveats remain. Some names coincide with, or consist of, perfectly valid words that are present in the Dutch dictionary. To mitigate this, some blacklisting is applied:
 - A phrase of the form 'van den <something>' or 'van der <something>' is assumed to be a last name and masked.
 - A phrase of the form '<masked> van|aan|in de|het|t <something>' is assumed to be a first + last name (where the first name has already been caught). This mask inevitably has a tendency to mask things that are not names, and can hopefully be improved in the future. For now this problem is mitigated by applying this mask only if the phrase does not contain any words on the domain-specific whitelist.
 - A specific curated blacklist is provided. Any word or phrase on this blacklist is always masked.

## Future additions

#### Numbers that are not digits

This package was designed primarily with chat transcripts in mind. With such user-typed data, sensitive numbers will generally be digits because they are faster to type (e.g. 1983 instead of negentien drieëntachtig). However, this may not be the case with e.g. text generated by speech-to-text software. It may be desirable to blacklist such written-out numbers.









