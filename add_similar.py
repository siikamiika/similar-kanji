#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from file.similars_file import SimilarsFile

FILENAME = 'kanji.tgz_similars.ut8'

def main():
    similar = SimilarsFile(FILENAME)
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
            new = input('Similar to {}:'.format(kanji)).strip()
            if len(new) == 1:
                similar.set_similar(kanji, new)
                print('{}: '.format(kanji) + ', '.join(similar.get_similar(kanji)))
            elif len(new) == 0:
                kanji = None
                break
            else:
                print('invalid input')

    similar.write()

if __name__ == '__main__':
    main()
