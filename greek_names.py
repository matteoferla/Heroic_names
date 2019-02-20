#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__description__ = \
    """
A small script to find 
NB. Written for python 3, not tested under 2.
"""
__author__ = "Matteo Ferla. [Github](https://github.com/matteoferla)"
__email__ = "matteo.ferla@gmail.com"
__date__ = ""
__license__ = "Cite me!"
__version__ = "1.0"

import urllib.request
import pickle, os, re, csv
from collections import Counter

#https://www.ssa.gov/oact/babynames/limits.html

def iternames():
    for file in os.listdir('names'):
        if file.find('yob') == -1:
            continue
        year=int(re.search('(\d+)',file).group(1))
        print(year)
        for row in open(os.path.join('names',file)):
            if not row:
                continue
            (name,gender,freq)=row.rstrip().split(',')
            yield (year,name,gender,freq)

def get_heroes(filename):
    greeks = set()
    for row in open(filename, encoding="utf-8"):
        srow = row.rstrip().replace('Äé', ' ').replace(',', ' ').replace(' ', ' ').split()
        if not srow:
            continue
        name = srow[0].title().replace('ä', 'a').replace('ö', 'o').replace('ë', 'e').replace('ü', 'u')
        if len(name) < 2:
            continue
        greeks.add(name)
    return greeks

def find_heroes(filename):
    # prep
    greeks=get_heroes(filename)
    yeardex={hero: {year: 0 for year in range(1880,2018)} for hero in greeks}
    genderdex={hero: {'M': 0,'F': 0} for hero in greeks}
    ## parse all data
    for (year,name,gender,freq) in iternames():
        if name in greeks:
            genderdex[name][gender]+=int(freq)
            yeardex[name][year]+=int(freq) # combine genders
    # write table
    with open(filename.replace('.txt','.csv'),'w', newline='') as w:
        writer=csv.DictWriter(w,['Hero','M','F','T']+list(range(1880,2018)))
        writer.writeheader()
        for hero in greeks:
            writer.writerow({'Hero': hero,
                             'M': genderdex[hero]['M'],
                             'F': genderdex[hero]['F'],
                             'T': genderdex[hero]['M'] + genderdex[hero]['F'],
                             **yeardex[hero]
                             })

def get_heroic_distribution(greeks):
    lettercount={'M':Counter(),'F':Counter()}
    for (year, name, gender, freq) in iternames():
        if name in greeks:
            lettercount[gender].update([len(name)])
    return lettercount


def get_distribution():
    lettercount={'M':Counter(),'F':Counter()}
    for (year, name, gender, freq) in iternames():
        lettercount[gender].update([len(name)])
    return lettercount

def print_distribution(lettercount):
    print('N', 'M','F')
    for i in range(1, 20):
        print(i, lettercount['M'][i], lettercount['F'][i])


if __name__ == '__main__':
    #print_distribution(get_distribution())
    greeks=get_heroes('greeks.txt')
    print_distribution(get_heroic_distribution(greeks))
    #find_heroes('iliad.txt')






