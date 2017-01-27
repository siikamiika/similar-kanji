#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from file.similars_file import SimilarsFile
from file.not_similar_file import NotSimilar

FILENAME = 'kanji.tgz_similars.ut8'

def main():
    similar = SimilarsFile(FILENAME)
    not_similar = NotSimilar()
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
                not_similar.add(kanji, remove)
                print('{}: '.format(kanji) + ', '.join(similar.get_similar(kanji)))
            elif len(remove) == 0:
                kanji = None
                break
            else:
                print('invalid input')

    similar.write()
    not_similar.write()

if __name__ == '__main__':
    main()
