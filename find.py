#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from os.path import dirname, realpath
from itertools import combinations
from file.kanjidic2 import Kanjidic2
from file.radkfile import Radkfile
from file.similars_file import SimilarsFile
from file.not_similar_file import NotSimilar

os.chdir(dirname(realpath(__file__)))

class SimilarFinder(object):

    def __init__(self, radkfile, kanjidic):
        self.radkfile = radkfile
        self.kanjidic = kanjidic
        self.similar = SimilarsFile('kanji.tgz_similars.ut8')
        self.not_similar = NotSimilar()
        self.kanjidic_parsed = self._kanjidic_parsed()

    def find_not_similar(self):
        self.not_similar_ignore = NotSimilar('not_similar_ignore')
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
                if add_all or self._match(kanji, similar):
                    queued.append((kanji, similar))

        queued = list(filter(lambda q:
            not (q[0] not in self.similar.get_similar(q[1])
            or q[0] in self.not_similar_ignore.get(q[1])), queued))
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

    def find_similar(self):
        queued = []
        for kanji1, kanji2 in combinations(self.kanjidic_parsed, 2):
            if self._match(kanji1, kanji2):
                queued.append((kanji1, kanji2))

        queued = list(filter(lambda q:
            not (q[0] in self.similar.get_similar(q[1])
            or q[0] in self.not_similar.get(q[1])), queued))
        print(len(queued))

        i = None
        for kanji1, kanji2 in queued:
            if kanji1 in self.similar.get_similar(kanji2) or kanji1 in self.not_similar.get(kanji2):
                continue
            if i == 'a':
                break
            i = input('Do {} and {} look similar? (Y(es)/n(o)/a(bort)):'.format(kanji1, kanji2))
            if i == 'a':
                break
            if i == 'n':
                self.not_similar.add(kanji1, kanji2)
            else:
                self.similar.set_similar(kanji1, kanji2)

        self.similar.write()
        self.not_similar.write()

    def _kanjidic_parsed(self):
        parsed = dict()
        for k in self.kanjidic.dic:
            kanji = self.kanjidic.get(k)
            if kanji and (kanji['grade'] or kanji['freq']):
                parsed[k] = kanji
        return parsed

    def _match(self, kanji1, kanji2):
        kanji1_parts = self.radkfile.krad.get(kanji1)
        kanji2_parts = self.radkfile.krad.get(kanji2)
        if not (kanji1_parts and kanji2_parts):
            return False

        if args.not_radicals and set(args.not_radicals) & (kanji1_parts | kanji2_parts):
            return False

        if args.only_radicals and not set(args.only_radicals) <= (kanji1_parts & kanji2_parts):
            return False

        if args.some_radicals:
            some = set(args.some_radicals)
            if not (some & kanji1_parts and some & kanji2_parts):
                return False

        kanji1 = self.kanjidic_parsed[kanji1]
        kanji2 = self.kanjidic_parsed[kanji2]

        def _radical_diff():
            if args.radical_diff == None:
                return True
            rad_diff = len(kanji1_parts ^ kanji2_parts)
            if args.radical_diff > 0:
                return rad_diff >= args.radical_diff
            else:
                return rad_diff <= -args.radical_diff

        def _strokecount_diff():
            if args.strokecount_diff == None:
                return True
            sc_diff = abs(kanji1['stroke_count'] - kanji2['stroke_count'])
            if args.strokecount_diff > 0:
                return sc_diff >= args.strokecount_diff
            else:
                return sc_diff <= -args.strokecount_diff
        def _skip():
            skip_match = True
            if args.same_skip1:
                skip_match = kanji1['skip'][0] != kanji2['skip'][0]
            elif args.skip1_are:
                skip_match = tuple(sorted([kanji1['skip'][0], kanji2['skip'][0]])) == tuple(sorted(args.skip1_are))
            return skip_match

        return _radical_diff() and _strokecount_diff() and _skip()

def main():
    kanjidic2 = Kanjidic2()
    radkfile = Radkfile()
    similar_finder = SimilarFinder(radkfile, kanjidic2)
    if args.add:
        similar_finder.find_similar()
    elif args.remove:
        similar_finder.find_not_similar()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--remove', action='store_true')
    parser.add_argument('--only-radicals', '-o', nargs='*')
    parser.add_argument('--some-radicals', '-sr', nargs='*')
    parser.add_argument('--not-radicals', '-n', nargs='*')
    parser.add_argument('--strokecount-diff', '-s', type=int, nargs='?')
    parser.add_argument('--radical-diff', '-r', type=int, nargs='?')
    parser.add_argument('--same-skip1', '-ss1', action='store_true')
    parser.add_argument('--skip1-are', '-s1', type=int, nargs='*')
    parser.add_argument('--similar-count-max', '-sc', type=int, nargs='?')
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--no', action='store_true')
    args = parser.parse_args()
    if not (args.add or args.remove):
        parser.error('--add or --remove required')
    main()
