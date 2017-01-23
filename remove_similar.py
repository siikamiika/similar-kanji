#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from file.similars_file import SimilarsFile

FILENAME = 'kanji.tgz_similars.ut8'
NOT_SIMILAR = 'not_similar'

def main():
    similar = SimilarsFile(FILENAME)
    try:
        with open(NOT_SIMILAR) as f:
            not_similar = json.load(f)
    except:
        not_similar = dict()
    kanji = None

    while True:
        if not kanji:
            user_input = input('Enter kanji to modify or q(uit):').strip()
            if user_input == 'q':
                break
            elif len(user_input) == 1:
                kanji = user_input
            continue

        print('Empty input to stop editing this kanji')
        print('{}: '.format(kanji) + ', '.join(similar.get_similar(kanji)))
        while True:
            remove = input('Not similar to {}:'.format(kanji)).strip()
            if len(remove) == 1:
                similar.remove_similar(kanji, remove)
                if not not_similar.get(kanji):
                    not_similar[kanji] = [remove]
                elif not remove in not_similar[kanji]:
                    not_similar[kanji].append(remove)
                if not not_similar.get(remove):
                    not_similar[remove] = [kanji]
                elif not kanji in not_similar[remove]:
                    not_similar[remove].append(kanji)
                print('{}: '.format(kanji) + ', '.join(similar.get_similar(kanji)))
            elif len(remove) == 0:
                kanji = None
                break
            else:
                print('invalid input')

    similar.write()
    with open('not_similar', 'w') as f:
        json.dump(not_similar, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
