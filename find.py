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
from file.kanjivg_parts import KanjiVGParts
import json

os.chdir(dirname(realpath(__file__)))

class SimilarFinder(object):

    def __init__(self):
        self.radkfile = Radkfile()
        self.kanjidic = Kanjidic2()
        self.kanjivg_parts = KanjiVGParts()
        self.similar = SimilarsFile('kanji.tgz_similars.ut8')
        self.not_similar = NotSimilar()
        self.kanjidic_parsed = self._kanjidic_parsed()
        with open('similar_parts.json', encoding='utf-8') as f:
            similar_parts_raw = json.load(f)
        self.similar_parts = dict()
        for p1, p2 in similar_parts_raw:
            for p in p1, p2:
                if not self.similar_parts.get(p):
                    self.similar_parts[p] = []
            if not p2 in self.similar_parts[p1]:
                self.similar_parts[p1].append(p2)
            if not p1 in self.similar_parts[p2]:
                self.similar_parts[p2].append(p1)

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
        if args.print:
            for q in queued:
                print(''.join(q))

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
        if args.print:
            for q in queued:
                print(''.join(q))

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
            if kanji and ((kanji['grade'] and kanji['grade'] < 10) or kanji['freq']):
                parsed[k] = kanji
        return parsed

    def _match(self, kanji1, kanji2):

        # general
        if args.kanji1_in:
            if kanji2 in args.kanji1_in:
                kanji1, kanji2 = kanji2, kanji1
            elif kanji1 not in args.kanji1_in:
                return False

        if args.only_kanji:
            for k in kanji1, kanji2:
                if k not in args.only_kanji:
                    return False

        # radkfile
        kanji1_radicals = kanji2_radicals = None
        if args.not_radicals or args.only_radicals or args.some_radicals or args.radical_diff is not None:
            kanji1_radicals = self.radkfile.krad.get(kanji1)
            kanji2_radicals = self.radkfile.krad.get(kanji2)

            if not (kanji1_radicals and kanji2_radicals):
                return False

            if args.not_radicals and set(args.not_radicals) & (kanji1_radicals | kanji2_radicals):
                return False

            if args.only_radicals and not set(args.only_radicals) <= (kanji1_radicals & kanji2_radicals):
                return False

            if args.some_radicals:
                some = set(args.some_radicals)
                if not (some & kanji1_radicals and some & kanji2_radicals):
                    return False

        def _radical_diff():
            if args.radical_diff == None:
                return True
            rad_diff = len(kanji1_radicals ^ kanji2_radicals)
            if args.radical_diff > 0:
                return rad_diff >= args.radical_diff
            else:
                return rad_diff <= -args.radical_diff

        # kanjivg
        kanji1_parts = kanji2_parts = None
        if args.not_parts or args.only_parts or args.some_parts or args.part_diff is not None:
            kanji1_parts = self.kanjivg_parts.get_parts(kanji1)
            kanji2_parts = self.kanjivg_parts.get_parts(kanji2)

            if not (kanji1_parts and kanji2_parts):
                return False

            if args.not_parts and set(args.not_parts) & (kanji1_parts | kanji2_parts):
                return False

            if args.only_parts and not set(args.only_parts) <= (kanji1_parts & kanji2_parts):
                return False

            if args.some_parts:
                some = set(args.some_parts)
                if not (some & kanji1_parts and some & kanji2_parts):
                    return False

        def _part_diff():
            if args.part_diff == None:
                return True

            k1 = kanji1
            k2 = kanji2
            p1 = kanji1_parts
            p2 = kanji2_parts

            if k1 in p2:
                p1 = set([k1])
            elif k2 in p1:
                p2 = set([k2])

            if args.use_similar_parts:
                part_diff = 0

                def get_skip(entry):
                    entry = self.kanjidic_parsed.get(entry)
                    if entry and entry.get('skip'):
                        return entry['skip'][0]
                    else:
                        return -1

                p2, p1 = sorted([p1, p2], key=len)
                for _p1 in p1:
                    similar_part = False
                    _p1_skip1 = get_skip(_p1)
                    _p1_deep = set([_p1] + list(filter(lambda k: get_skip(k) == _p1_skip1, self.similar.get_similar(_p1))))
                    if self.similar_parts.get(_p1):
                        _p1_deep |= set(self.similar_parts[_p1])
                    for _p2 in p2:
                        _p2_skip1 = get_skip(_p2)
                        _p2_deep = set([_p2] + list(filter(lambda k: get_skip(k) == _p2_skip1, self.similar.get_similar(_p2))))
                        if self.similar_parts.get(_p2):
                            _p2_deep |= set(self.similar_parts[_p2])
                        if args.use_similar_parts_deep:
                            if _p1_deep & _p2_deep:
                                similar_part = True
                                break
                        else:
                            if _p1 in _p2_deep or _p2 in _p1_deep:
                                similar_part = True
                                break
                    if not similar_part:
                        part_diff += 1
            else:
                part_diff = len(kanji1_parts ^ kanji2_parts)
            if args.part_diff > 0:
                return part_diff >= args.part_diff
            else:
                return part_diff <= -args.part_diff

        # kanjidic2
        kanjidic_kanji1 = self.kanjidic_parsed[kanji1]
        kanjidic_kanji2 = self.kanjidic_parsed[kanji2]

        def _strokecount_diff():
            if args.strokecount_diff == None:
                return True
            sc_diff = abs(kanjidic_kanji1['stroke_count'] - kanjidic_kanji2['stroke_count'])
            if args.strokecount_diff > 0:
                return sc_diff >= args.strokecount_diff
            else:
                return sc_diff <= -args.strokecount_diff

        def _skip():
            skip_match = True
            skip_1 = kanjidic_kanji1['skip'][0] if kanjidic_kanji1.get('skip') else -1
            skip_2 = kanjidic_kanji2['skip'][0] if kanjidic_kanji2.get('skip') else -1
            if args.same_skip1:
                skip_match = skip_1 != skip_2
            elif args.skip1_are:
                skip_match = tuple(sorted([skip_1, skip_2])) == tuple(sorted(args.skip1_are))
            return skip_match

        return (_skip()
                and _radical_diff()
                and _part_diff()
                and _strokecount_diff())

def main():
    similar_finder = SimilarFinder()
    if args.add:
        similar_finder.find_similar()
    elif args.remove:
        similar_finder.find_not_similar()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # mode
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--remove', action='store_true')
    # print
    parser.add_argument('--print', action='store_true')
    # radkfile
    parser.add_argument('--only-radicals', '-o', nargs='*')
    parser.add_argument('--some-radicals', '-sr', nargs='*')
    parser.add_argument('--not-radicals', '-n', nargs='*')
    parser.add_argument('--radical-diff', '-r', type=int, nargs='?')
    # kanjidic2
    parser.add_argument('--strokecount-diff', '-s', type=int, nargs='?')
    parser.add_argument('--same-skip1', '-ss1', action='store_true')
    parser.add_argument('--skip1-are', '-s1', type=int, nargs='*')
    # kanjivg
    parser.add_argument('--only-parts', '-op', nargs='*')
    parser.add_argument('--some-parts', '-sp', nargs='*')
    parser.add_argument('--not-parts', '-np', nargs='*')
    parser.add_argument('--part-diff', '-p', type=int, nargs='?')
    parser.add_argument('--use-similar-parts', '-usp', action='store_true')
    parser.add_argument('--use-similar-parts-deep', '-uspd', action='store_true')
    # general
    parser.add_argument('--similar-count-max', '-sc', type=int, nargs='?')
    parser.add_argument('--kanji1-in', '-k1', nargs='*')
    parser.add_argument('--only-kanji', '-ok', nargs='*')
    # no user interaction
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--no', action='store_true')
    args = parser.parse_args()
    if not (args.add or args.remove):
        parser.error('--add or --remove required')
    main()
