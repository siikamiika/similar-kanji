#!/usr/bin/env python3

import json
import sys
from itertools import combinations
from file.similars_file import SimilarsFile
from file.not_similar_file import NotSimilar

def main():

    with open(sys.argv[1]) as f:
        data = json.load(f)
    similar = SimilarsFile('kanji.tgz_similars.ut8')
    not_similar = NotSimilar()

    queue = []
    skipped = 0
    for group in data:
        for c1, c2 in combinations(group, 2):
            if c1 not in similar.get_similar(c2) and c1 not in not_similar.get(c2):
                queue.append((c1, c2))
            else:
                skipped += 1

    auto = False
    if len(sys.argv) > 2 and sys.argv[2] == 'auto':
        auto = True

    for pair in queue:
        print(''.join(pair))
    print(len(queue))
    print('skipped: {}'.format(skipped))
    for c1, c2 in queue:
        if c1 in similar.get_similar(c2):
            continue
        if auto:
            similar.set_similar(c1, c2)
        else:
            i = input('Do {} and {} look similar? (Y/n/a(bort))'.format(c1, c2))
            if i == 'n':
                not_similar.add(c1, c2)
                continue
            if i == 'a':
                break
            else:
                similar.set_similar(c1, c2)

    similar.write()
    not_similar.write()

if __name__ == '__main__':
    main()
