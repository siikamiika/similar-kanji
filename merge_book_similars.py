#!/usr/bin/env python3
from file.similars_file import SimilarsFile
import json

def main():
    with open('book-similars.txt') as f:
        data = json.load(f)
    similar = SimilarsFile('kanji.tgz_similars.ut8')
    for group in data:
        for c1 in group:
            for c2 in group:
                similar.set_similar(c1, c2)
    similar.write()

if __name__ == '__main__':
    main()
