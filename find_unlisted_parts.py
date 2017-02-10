#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import combinations
from file.similars_file import SimilarsFile
from file.kanjivg_parts import KanjiVGParts
import json

def main():

    similar = SimilarsFile('kanji.tgz_similars.ut8')

    kanjivg_parts = KanjiVGParts()

    with open('similar_parts.json', encoding='utf-8') as f:
        similar_parts_raw = json.load(f)
    similar_parts = dict()
    for p1, p2 in similar_parts_raw:
        for p in p1, p2:
            if not similar_parts.get(p):
                similar_parts[p] = []
        if not p2 in similar_parts[p1]:
            similar_parts[p1].append(p2)
        if not p1 in similar_parts[p2]:
            similar_parts[p2].append(p1)


    results = []
    for k in similar.kanji:
        parts = kanjivg_parts.get_parts(k)
        if not parts:
            continue
        for part in parts:
            if part not in list(similar.kanji) + list(kanjivg_parts.kanji):
                if part not in results:
                    results.append(part)

    with open('unlisted_parts.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
