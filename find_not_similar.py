#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from os.path import dirname, realpath
from file.kanjidic2 import Kanjidic2
from file.radkfile import Radkfile
from file.similars_file import SimilarsFile
from file.not_similar_file import NotSimilar

os.chdir(dirname(realpath(__file__)))

class NotSimilarFinder(object):

    def __init__(self, radkfile, kanjidic):
        self.radkfile = radkfile
        self.kanjidic = kanjidic
        self.similar = SimilarsFile('kanji.tgz_similars.ut8')
        self.not_similar = NotSimilar()
        self.not_similar_ignore = NotSimilar('not_similar_ignore')
        self.kanjidic_parsed = self._kanjidic_parsed()

    def start(self):
        queued = []
        for kanji in self.similar.kanji:
            add_all = False
            if args.similar_count_max and len(self.similar.get_similar(kanji)) > args.similar_count_max:
                add_all = True
            if kanji not in self.kanjidic_parsed:
                continue
            for similar in self.similar.get_similar(kanji):
                if similar not in self.kanjidic_parsed:
                    continue
                if add_all or self._not_similar(kanji, similar):
                    queued.append((kanji, similar))
        print(len(queued))
        for kanji, similar in queued:
            if similar not in self.similar.get_similar(kanji) or similar in self.not_similar_ignore.get(kanji):
                continue
            print('{}: {}'.format(kanji, ', '.join(self.similar.get_similar(kanji))))
            if args.yes:
                i = 'Y'
            elif args.no:
                i = 'n'
            else:
                i = input('Do {} and {} look different? (Y(es)/n(o)/a(bort)):'.format(kanji, similar))
            if i == 'a':
                break
            if i == 'n':
                self.not_similar_ignore.add(kanji, similar)
                continue
            else:
                self.similar.remove_similar(kanji, similar)
                self.not_similar.add(kanji, similar)

        self.similar.write()
        self.not_similar.write()
        self.not_similar_ignore.write()

    def _kanjidic_parsed(self):
        parsed = dict()
        for k in self.kanjidic.dic:
            kanji = self.kanjidic.get(k)
            if kanji and (kanji['grade'] or kanji['freq']):
                parsed[k] = kanji
        return parsed

    def _not_similar(self, kanji1, kanji2):
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

        skip_match = True
        if args.same_skip1:
            skip_match = kanji1['skip'][0] != kanji2['skip'][0]
        elif args.skip1_are:
            skip_match = tuple(sorted([kanji1['skip'][0], kanji2['skip'][0]])) == tuple(sorted(args.skip1_are))

        return (len(kanji1_parts ^ kanji2_parts) <= (args.radical_diff or 9001)
            and strokecount_diff >= (args.strokecount_diff or 0)
            and (kanji1['skip'][0] != kanji2['skip'][0] if args.same_skip1 else True)
            and skip_match)

def main():
    kanjidic2 = Kanjidic2()
    radkfile = Radkfile()
    similar_finder = NotSimilarFinder(radkfile, kanjidic2)
    similar_finder.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Help remove not similar kanji from kanji.tgz_similars.ut8.')
    parser.add_argument('--only-radicals', '-o', nargs='*')
    parser.add_argument('--not-radicals', '-n', nargs='*')
    parser.add_argument('--strokecount-diff', '-s', type=int, nargs='?')
    parser.add_argument('--radical-diff', '-r', type=int, nargs='?')
    parser.add_argument('--same-skip1', '-ss1', action='store_true')
    parser.add_argument('--skip1-are', '-s1', type=int, nargs='*')
    parser.add_argument('--similar-count-max', '-sc', type=int, nargs='?')
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--no', action='store_true')
    args = parser.parse_args()
    main()
