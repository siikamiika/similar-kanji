#!/usr/bin/env python3
from file.similars_file import SimilarsFile

def main():
    similar = SimilarsFile('kanji.tgz_similars.ut8')
    for kanji in similar.kanji:
        try:
            similar.kanji[kanji].remove(kanji)
        except:
            pass
    similar.write()

if __name__ == '__main__':
    main()
