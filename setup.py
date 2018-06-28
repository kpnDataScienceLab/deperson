# (c) KPN B.V. 
# Licensed under MIT License (see LICENSE.txt)
# Author: Marco Tompitak, Text Analytics Group, KPN Data Science Lab

from distutils.core import setup

setup(name='deperson',
      version='0.1',
      description='Package for depersonalizing text data in Dutch',
      author='Marco Tompitak',
      author_email='marco.tompitak@kpn.com',
      url='https://github.com/kpnDataScienceLab/deperson',
      packages=['deperson'],
      install_requires=['hunspell',
                        'unidecode',
                        'pandas',
                        ],
      package_data={'deperson':
                    ['dict/*.aff',
                     'dict/*.dic',
                     'spellcheck/*.csv',
                     'whitelists/*.txt',
                     'blacklists/*.txt',
                     ]},
      scripts=['scripts/deperson_pickle.py',
               'scripts/illegal_words_from_pickle.py',
               ],
      )
