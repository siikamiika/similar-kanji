#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import sys
import json
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

        kanji1 = self.kanjidic_parsed[kanji1]
        kanji2 = self.kanjidic_parsed[kanji2]

        strokecount_diff = abs(kanji1['stroke_count'] - kanji2['stroke_count'])

        return len(kanji1_parts ^ kanji2_parts) <= 2 and strokecount_diff <= 2

def main():
    kanjidic2 = Kanjidic2()
    radkfile = Radkfile()
    similar_finder = SimilarFinder(radkfile, kanjidic2)
    similar_finder.start()

if __name__ == '__main__':
    main()
