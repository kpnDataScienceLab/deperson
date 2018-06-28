#!/usr/bin/env python

# (c) KPN B.V. 
# Licensed under MIT License (see LICENSE.txt)
# Author: Marco Tompitak, Text Analytics Group, KPN Data Science Lab

import argparse
import pandas as pd
# from deperson.deperson import Deperson
import sys
sys.path.insert(0, './deperson')

from deperson import Deperson

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Get illegal words from pickled dataframe.')

parser.add_argument('-d', '--datafile', dest='datafile', required=True)
parser.add_argument('-o', '--output', dest='outfile', default='stdout',
                    help='Output file to store results.')
parser.add_argument('-f', '--field', dest='field', default='masked_text',
                    help='Field to mask.')
parser.add_argument('-a', '--autocorrect', dest='autocorrect',
                    default=False, action='store_true',
                    help='Whether to apply autocorrection.')
parser.add_argument('-e', '--check-compound-words', dest='check_compound',
                    default=False, action='store_true',
                    help='Whether to check for long compound words.')

args = parser.parse_args()

# Depersonalizer
d = Deperson(autocorrect=args.autocorrect, check_compound=args.check_compound)

# Read in data
with open(args.datafile, 'rb') as f:
    data = pd.read_pickle(f)[['LiveChatButtonId', 'cleaned_text']].dropna()

# Get all illegal words in a single string
illegal = data[args.field].apply(lambda text: d.get_illegal_words(text)).str.cat(sep=' ')

# Save result
if args.outfile == 'stdout':
    print(illegal)
else:
    with open(args.outfile, 'w') as f:
        f.write(illegal)
