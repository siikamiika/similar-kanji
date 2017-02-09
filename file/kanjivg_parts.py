#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import time
from os.path import isfile

class KanjiVGParts(object):

    CACHE = 'kanjivgparts.pickle'

    def __init__(self):
        if isfile(KanjiVGParts.CACHE):
            print('loading KanjiVG parts from cache...')
            start = time.time()
            with open(KanjiVGParts.CACHE, 'rb') as f:
                self.kanji = pickle.load(f)
            print('    loaded in {:.2f} s'.format(time.time() - start))
        else:
            raise 'kanjivgparts.pickle not found'

    def get_parts(self, kanji):
        return set(self.kanji.get(kanji) or [])

    def get_combinations(self, parts):
        combinations = []

        for k in self.kanji:
            if parts.issubset(self.kanji[k]):
                combinations.append(k)

        return combinations
