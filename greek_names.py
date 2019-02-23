#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__description__ = \
    """
A small script to find greek names.
See class HeroicNames for more.
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

import sys
from warnings import warn

if sys.version_info[0] < 3:
    warn("Sorry man, I told you to use Python 3.")


##############################################################################

class HeroicNames:
    """
    Make intance with nothing, iterable or file of greek names. can be messy. But one greek per line.
    The attribute `.greeks` is the set of names.
    The iterator iternames() runs through the files. Really fast surprisingly.
    While iterating through an intsnace of this class runs thorugh the greeks set.
    parse() parses the census for the greeks stored and makes the.census attribute. This ought to be a class, but shmeh
    key = hero: value = {1880: {'M': n, 'F': f, 'T': t}, ..., 'total': {'M':m, ...}}
    To add a greek afterwards use `.add_name(name)` not .`greeks.add(name)` due to the .census

    """
    groups = ('greeks','greeks_freq','census', 'census_freq')
    genders = ('T', 'M', 'F')

    def __init__(self, iterable=None, filename=None):
        """
        Initialises the name holding instance. `.greeks` is the set.
        :param iterable: opt.
        :param filename: opt.
        """
        self.greeks = set()
        self.census = {}  # key = hero: value = {year: {'M': n, 'F': f}} #not a default dictionary due to the tallies.
        if filename:
            with open(filename, encoding="utf-8") as w:
                for row in w:
                    self.add_name(row)
        if iterable:
            for row in iterable:
                self.add_name(row)

    def __iter__(self):
        return self.greeks.__iter__()

    def add_name(self, row):
        """
        cleans and saves the anme
        :param row: No name should have spaces or unicode.
        :return:
        """
        srow = row.rstrip().replace('Äé', ' ').replace(',', ' ').replace(' ', ' ').split()
        if not srow:
            return self
        name = srow[0].title().replace('ä', 'a').replace('ö', 'o').replace('ë', 'e').replace('ü', 'u')
        if len(name) < 2:
            return self
        self.greeks.add(name)
        # fill.census.
        if name not in self.census:
            self.census[name] = {year: {'M': 0, 'F': 0, 'T': 0} for year in range(1880, 2018)}
            self.census[name]['total'] = {'M': 0, 'F': 0, 'T': 0}
        return self

    @staticmethod
    def iternames():
        """iterates across census not greeks.
        https://www.ssa.gov/oact/babynames/limits.html"""
        for file in os.listdir('names'):
            if file.find('yob') == -1:
                continue
            year = int(re.search('(\d+)', file).group(1))
            print(year)
            with open(os.path.join('names', file)) as fh:
                for row in fh:
                    if not row:
                        continue
                    (name, gender, freq) = row.rstrip().split(',')
                    yield (year, name, gender, freq)

    def _count(self, name, year, gender, freq=0):
        # adds to the count
        amount = int(freq)
        self.census[name][year][gender] = amount
        self.census[name][year]['T'] += amount
        self.census[name]['total'][gender] += amount
        self.census[name]['total']['T'] += amount
        return self

    def parse(self):
        """
        looks for the greeks in the census and adds them to .census
        :return:
        """
        for (year, name, gender, freq) in self.iternames():
            if name in self.greeks:
                self._count(name, year, gender, freq)
        return self

    def write(self, filename):
        with open(filename, 'w', newline='') as w:
            writer = csv.DictWriter(w, ['Hero', 'grantotal', 'male_total', 'female_total'] +
                                    ['{g}_{i}'.format(g=g, i=i) for g in self.genders for i in range(1880, 2018)])
            writer.writeheader()
            for hero in self:
                writer.writerow({'Hero': hero,
                                 'male_total': self.census[hero]['total']['M'],
                                 'female_total': self.census[hero]['total']['F'],
                                 'grantotal': self.census[hero]['total']['T'],
                                 **{'{g}_{i}'.format(g=g, i=i):
                                        self.census[hero][i][g] for g in self.genders for i in range(1880, 2018)}
                                 })
        return self

    def get_lettercount(self):
        # groups ('greeks','greeks_freq','census', 'census_freq')
        lettercount = {group: {'M': Counter(), 'F': Counter(), 'T': Counter()} for group in self.groups}
        for (year, name, gender, freq) in self.iternames():
            lettercount['census'][gender].update([len(name)])
            lettercount['census_freq'][gender][len(name)] += int(freq)
            lettercount['census_freq']['T'][len(name)] += int(freq)
            lettercount['census']['T'].update([len(name)]) #this value is wrong. As the same name as name and female gets counted.
            if name in self:
                lettercount['greeks'][gender].update([len(name)])
                lettercount['greeks_freq'][gender][len(name)] += int(freq)
                lettercount['census_freq']['T'][len(name)] += int(freq)
                lettercount['census']['T'].update([len(name)]) #issue.
        return lettercount


    @classmethod
    def write_lettercount(cls, lettercount, filename):
        with open(filename, 'w',newline='') as w:
            d=csv.DictWriter(w, fieldnames=['N']+[group+'_'+gen for gen in cls.genders for group in cls.groups])
            d.writeheader()
            for i in range(1, 20):
                d.writerow({'N':i,
                            **{group + '_' + gen: lettercount[group][gen][i] for gen in cls.genders for group in cls.groups}
                })
        return cls


if __name__ == '__main__':
    print('General distribution')
    hero = HeroicNames(filename='greeks.txt').parse().write('greeks.csv')
    print('Lettercount')
    l = hero.get_lettercount() #get is a getter...
    HeroicNames.write_lettercount(l,'greek_distro.csv')