#!/usr/bin/env python

# (c) KPN B.V. 
# Licensed under MIT License (see LICENSE.txt)
# Author: Marco Tompitak, Text Analytics Group, KPN Data Science Lab

import argparse
import pandas as pd
from deperson.deperson import Deperson


# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Depersonalize a pickled dataframe.')

parser.add_argument('-d', '--datafile', dest='datafile', required=True)
parser.add_argument('-o', '--output', dest='outfile', default='overwrite',
                    help='Output file to store results.')
parser.add_argument('-f', '--field', dest='field', default='masked_text',
                    help='Field to mask.')
parser.add_argument('-r', '--rename-field', dest='rfield',
                    default='masked_text', help='New name for field.')
parser.add_argument('-c', '--drop-original-column', dest='dropcol',
                    default=False, action='store_true',
                    help='Whether to drop original column.')
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
data = pd.read_pickle(args.datafile)

# Mask field
data['masked_text'] = data[args.field].apply(
    lambda text: d.apply_blacklist(d.apply_whitelist(text)))

# Drop original column if requested
if args.dropcol:
    data = data.drop(args.field, axis=1)

# Output
if args.outfile == 'overwrite':
    data.to_pickle(args.datafile)
else:
    data.to_pickle(args.outfile)
