#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import sys
import json
import argparse
from os.path import dirname, realpath
from file.kanjidic2 import Kanjidic2
from file.radkfile import Radkfile

os.chdir(dirname(realpath(__file__)))

class SimilarFinder(object):

    def __init__(self, radkfile, kanjidic):
        self.radkfile = radkfile
        self.kanjidic = kanjidic
        self.kanjidic_parsed = dict()
        self.kanji = self._valid_kanji()

    def start(self):
        for kanji1 in self.kanji:
            for kanji2 in self.kanji:
                if self._similar(kanji1, kanji2):
                    self.kanji[kanji1]['similar'].append(kanji2)

        with open('similar', 'w') as f:
            json.dump(self.kanji, f, ensure_ascii=False)

    def _valid_kanji(self):
        valid = dict()
        for k in self.kanjidic.dic:
            kanji = self.kanjidic.get(k)
            if kanji:
                if kanji['grade'] or kanji['freq']:
                    valid[kanji['literal']] = dict(similar=[])
                    self.kanjidic_parsed[k] = kanji
            else:
                print(k)
        print(len(valid))
        return valid

    def _similar(self, kanji1, kanji2):
        kanji1_parts = self.radkfile.krad.get(kanji1)
        kanji2_parts = self.radkfile.krad.get(kanji2)
        if not (kanji1_parts and kanji2_parts):
            return False

        if args.not_radicals and set(args.not_radicals) & (kanji1_parts | kanji2_parts):
            return False

        if args.only_radicals and not set(args.only_radicals) <= (kanji1_parts & kanji2_parts):
            return False

        kanji1 = self.kanjidic_parsed[kanji1]
        kanji2 = self.kanjidic_parsed[kanji2]

        strokecount_diff = abs(kanji1['stroke_count'] - kanji2['stroke_count'])

        return (len(kanji1_parts ^ kanji2_parts) <= (args.radical_diff or 9001)
            and strokecount_diff <= (args.strokecount_diff or 9001))

def main():
    kanjidic2 = Kanjidic2()
    radkfile = Radkfile()
    similar_finder = SimilarFinder(radkfile, kanjidic2)
    similar_finder.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Find similar kanji with the help of Radkfile and Kanjidic2.')
    parser.add_argument('--only-radicals', '-o', nargs='*')
    parser.add_argument('--not-radicals', '-n', nargs='*')
    parser.add_argument('--strokecount-diff', '-s', type=int, nargs='?')
    parser.add_argument('--radical-diff', '-r', type=int, nargs='?')
    args = parser.parse_args()
    main()
